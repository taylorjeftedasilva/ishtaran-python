"""
14 -- End-to-end marketplace journey, verified live against the real Sandbox (2026-08-25): a buyer
pays into a marketplace that holds its own self-custody execution wallet, a seller signs up as
their own AccountHolder to receive the payout, and the marketplace signs the real payout itself --
Ishtaran never sees a private key. Closes the full cycle other examples cover individually
(self-service signup, self-custody signing, Payment Intents, AccountHolder invitations): this one
connects them into one story, the way a real integrator would use them.

Two real gaps found and fixed while building this example, not hypothetical:
  - accounts.authorize_application requires a Member session -- it always rejects an API Key,
    even though Accounts is otherwise usable with either (see AccountsEndpoints.cs,
    MemberPermissionPolicy.Require).
  - Once a Payment Intent's deposit is confirmed, the Transaction moves itself to RESERVED -- no
    explicit transactions.reserve(...) call is needed (or valid) in this path.

Requires only ISHTARAN_ASSET_NETWORK_ID/ISHTARAN_NETWORK_ID env vars (an Asset Network already
seeded in the target Sandbox) -- everything else (Organization, Application, Environment, API Key,
both Accounts) is provisioned by the example itself.
"""

import os
import time
import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from ishtaran import Environment, IshtaranClient
from ishtaran.model.enums import DerivationScheme, TransactionStatus
from ishtaran.model.execution_custody import ExecutionLegInput
from ishtaran.model.data_plane import ParticipantInput
from ishtaran.wallet import generate as generate_wallet

asset_network_id = os.environ["ISHTARAN_ASSET_NETWORK_ID"]
network_id = os.environ["ISHTARAN_NETWORK_ID"]
t = int(time.time() * 1000)

# 1. Marketplace operator signs up -- one call provisions Organization, a default Application,
#    its Sandbox Environment, and a first API Key.
owner = IshtaranClient.create(environment=Environment.SANDBOX)
signup = owner.auth.sign_up(f"Marketplace Demo {t}", f"owner+{t}@example.com", "Str0ngP@ssw0rd!123")
organization_id, application_id, environment_id = signup.organization_id, signup.application_id, signup.environment_id
print("[1] signup ok organization_id=", organization_id)

client = IshtaranClient.create(api_key=signup.api_key_plain_text, environment=Environment.SANDBOX)

# 2. The marketplace's own execution wallet -- generated locally, only the public key ever
#    reaches Ishtaran. This is the wallet that will sign the real payout in step 9.
wallet = generate_wallet()
registered_wallet = client.wallets.register(
    application_id, network_id, DerivationScheme.TRON_BIP44_HARDENED_ACCOUNT,
    wallet.wallet.account_extended_public_key, f"marketplace-wallet-{t}",
)
print("[2] execution wallet registered wallet_id=", registered_wallet.wallet_id)

# 3. Seller signs up as their own AccountHolder, via an invitation the marketplace issues -- a
#    distinct session, never the marketplace acting on the seller's behalf.
invitation = client.accounts.create_account_holder_invitation(organization_id, f"seller-{t}")
seller_client = IshtaranClient.create(api_key=signup.api_key_plain_text, environment=Environment.SANDBOX)
claim = seller_client.account_holders.sign_up_and_claim_invitation(
    invitation.plain_text_token, f"seller+{t}@example.com", "SellerP@ss123!",
)
if not claim.success:
    raise RuntimeError(f"Seller failed to claim invitation: {claim.error_code}")
seller_account_id = seller_client.account_holders.me().account_id
print("[3] seller AccountHolder claimed, account_id=", seller_account_id)

# 4. Buyer account -- Organization-provisioned, no login of their own (the common case for a
#    one-off payer).
buyer_account_id = client.accounts.create(organization_id, f"buyer-{t}").account_id
print("[4] buyer account_id=", buyer_account_id)

# 5. Authorize both Accounts for this Application. GOTCHA: this call requires the Member session
#    (owner), not the API Key client (client) -- see module docstring.
owner.accounts.authorize_application(organization_id, seller_account_id, application_id)
owner.accounts.authorize_application(organization_id, buyer_account_id, application_id)
print("[5] both accounts authorized for the application")

# 6. Transaction + Payment Intent. No Split declared -- with exactly one non-payer Participant,
#    BR-SPL-004 gives that Participant 100% of the Distributable Amount implicitly (2+ non-payer
#    Participants would require an explicit Split).
payer = ParticipantInput(account_id=buyer_account_id, role="payer", is_payer=True, split_percentage=None)
seller = ParticipantInput(account_id=seller_account_id, role="seller", is_payer=False, split_percentage=None)
txn = client.transactions.create(organization_id, application_id, None, asset_network_id, Decimal("1000"), [payer, seller], f"marketplace-txn-{t}")
intent = client.deposits.create_payment_intent(organization_id, txn.transaction_id, asset_network_id, Decimal("1000"))
full_intent = client.deposits.get_payment_intent(intent.payment_intent_id)
print("[6] payment_intent_id=", intent.payment_intent_id, "deposit_address=", full_intent.deposit_address)

# 7. Simulate the buyer's on-chain deposit and its confirmation (Sandbox only). Once confirmed,
#    the Transaction moves itself to RESERVED -- no explicit reserve() call.
observed = client.sandbox.simulate_deposit(environment_id, full_intent.deposit_address, asset_network_id, Decimal("1000"))
client.sandbox.simulate_confirmation(environment_id, observed.sandbox_observed_address_id, 1, True)
status = TransactionStatus.CREATED
for _ in range(20):
    if status not in (TransactionStatus.CREATED, TransactionStatus.AWAITING_FUNDS):
        break
    time.sleep(1)
    status = client.transactions.get_state(txn.transaction_id).status
print("[7] deposit confirmed, transaction status=", status.name)

# 8. Settlement -- calculates the Platform Fee/Distributable split. It does not move funds by
#    itself; step 9 requests the real payout signature explicitly.
settlement = client.settlements.execute_settlement(txn.transaction_id)
print("[8] settlement executed id=", settlement.settlement_id)

# 9. The marketplace requests a SigningRequest for the real payout (seller's share, platform fee)
#    against its own execution wallet, and signs each leg's canonical hash LOCALLY -- the private
#    key is used here and only here, never sent anywhere.
allocated = client.wallets.allocate_deposit_address(application_id, network_id)
expires_at = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
legs = [
    ExecutionLegInput(role="Seller", destination_address="TSellerPayoutAddress0000000001", amount=Decimal("991")),
    ExecutionLegInput(role="PlatformFee", destination_address="TIshtaranFeeAddress00000000001", amount=Decimal("9")),
]
signing_request = client.signing_requests.create(
    environment_id, registered_wallet.wallet_id, allocated.derivation_reference,
    f"marketplace-settlement-{t}", asset_network_id, allocated.address, legs, expires_at,
    f"marketplace-sr-{t}",
)

for leg in client.signing_requests.get(signing_request.signing_request_id).legs:
    hash_bytes = bytes.fromhex(leg.canonical_hash)
    signature = wallet.signer.sign(allocated.derivation_reference, hash_bytes)
    result = client.signing_requests.submit_signed_transaction(
        signing_request.signing_request_id, leg.execution_leg_id, leg.canonical_hash, signature.hex().upper(),
    )
    # all_legs_verified only flips to True on the LAST leg submitted -- the all-signatures gate
    # never broadcasts on a partial set of signatures.
    print(f"[9] leg={leg.role} verified={result.verified} all_legs_verified={result.all_legs_verified}")

# 10. Confirm both legs broadcast -- the cycle is closed.
for leg in client.signing_requests.get(signing_request.signing_request_id).legs:
    print(f"[10] leg={leg.role} status={leg.status} broadcast_reference={leg.broadcast_reference}")
