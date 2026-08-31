"""
14 -- End-to-end marketplace journey, re-verified live 2026-08-31 against the Network Execution
Engine: a buyer pays into a marketplace that holds its own self-custody execution wallet, a seller
signs up as their own AccountHolder to receive the payout, and the marketplace signs the real
payout itself -- Ishtaran never sees a private key. Closes the full cycle other examples cover
individually (self-service signup, self-custody signing, Payment Intents, AccountHolder
invitations): this one connects them into one story, the way a real integrator would use them.

Real gaps found and fixed while building/re-validating this example, not hypothetical:
  - accounts.authorize_application requires a Member session -- it always rejects an API Key,
    even though Accounts is otherwise usable with either (see AccountsEndpoints.cs,
    MemberPermissionPolicy.Require).
  - Once a Payment Intent's deposit is confirmed, the Transaction moves itself to RESERVED -- no
    explicit transactions.reserve(...) call is needed (or valid) in this path.
  - execute_settlement() now builds its OWN SigningRequest automatically (confirmed live
    2026-08-31) -- an earlier version of this example manually called signing_requests.create()
    with hand-picked destination addresses right after execute_settlement(), which built a
    second, unrelated SigningRequest disconnected from the real Settlement. That is now wrong:
    sign the SigningRequest execute_settlement() itself returns (settlement.signing_request_id).
  - Under SelfCustody, broadcasting a beneficiary's leg costs real network resources, charged
    separately from the Platform Fee -- a NetworkCostPayerAccount must be registered once per
    (organization_id, asset_network_id) before the first real Settlement, or execute_settlement()
    fails with 422 PAYOUT_BATCH_NETWORK_COST_PAYER_ACCOUNT_NOT_REGISTERED. This example registers
    the marketplace's own commission Account as the payer -- a real business decision, not a
    technical afterthought.
  - Each beneficiary paid under SelfCustody (the seller, and the platform's own commission) needs
    a registered ExecutionDestination -- the real on-chain address that beneficiary actually
    receives funds at -- before execute_settlement() can build a leg for them.

Known gap, not fixed here: transactions.create(...) in this SDK has no environment_id parameter
at all (unlike the TypeScript SDK's equivalent) -- the backend does not hard-reject a Transaction
created this way, but it is semantically incomplete. Fixing it is out of scope for this example;
see SDK_CAPABILITY_SPEC.md item 10.

Requires only ISHTARAN_ASSET_NETWORK_ID/ISHTARAN_NETWORK_ID env vars (an Asset Network already
seeded in the target Sandbox) -- everything else (Organization, Application, Environment, API Key,
all three Accounts) is provisioned by the example itself.
"""

import os
import time
from decimal import Decimal

from ishtaran import Environment, IshtaranClient
from ishtaran.model.enums import DerivationScheme, TransactionStatus
from ishtaran.model.data_plane import ParticipantInput
from ishtaran.wallet import derive_tron_address, generate as generate_wallet

asset_network_id = os.environ["ISHTARAN_ASSET_NETWORK_ID"]
network_id = os.environ["ISHTARAN_NETWORK_ID"]
t = int(time.time() * 1000)


def sandbox_broadcast_attempt_id_from_reference(reference: str) -> str:
    prefix = "sandbox-broadcast-"
    if not reference.startswith(prefix):
        raise ValueError(f"Unexpected broadcastReference format: {reference}")
    hex_n = reference[len(prefix):]
    return f"{hex_n[0:8]}-{hex_n[8:12]}-{hex_n[12:16]}-{hex_n[16:20]}-{hex_n[20:32]}"

# 1. Marketplace operator signs up -- one call provisions Organization, a default Application,
#    its Sandbox Environment, and a first API Key.
owner = IshtaranClient.create(environment=Environment.SANDBOX)
signup = owner.auth.sign_up(f"Marketplace Demo {t}", f"owner+{t}@example.com", "Str0ngP@ssw0rd!123")
organization_id, application_id, environment_id = signup.organization_id, signup.application_id, signup.environment_id
print("[1] signup ok organization_id=", organization_id)

client = IshtaranClient.create(api_key=signup.api_key_plain_text, environment=Environment.SANDBOX)

# 2. The marketplace's own execution wallet -- generated locally, only the public key ever
#    reaches Ishtaran. This is the wallet that will sign the real payout in step 10, and that
#    allocates the marketplace's own commission address in step 6.
generated_wallet = generate_wallet()
registered_wallet = client.wallets.register(
    application_id, network_id, DerivationScheme.TRON_BIP44_HARDENED_ACCOUNT,
    generated_wallet.wallet.account_extended_public_key, f"marketplace-wallet-{t}",
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
#    one-off payer). The marketplace's own commission Account, same shape.
buyer_account_id = client.accounts.create(organization_id, f"buyer-{t}").account_id
marketplace_revenue_account_id = client.accounts.create(organization_id, f"marketplace-revenue-{t}").account_id
print("[4] buyer_account_id=", buyer_account_id, "marketplace_revenue_account_id=", marketplace_revenue_account_id)

# 5. Authorize all three Accounts for this Application. GOTCHA: this call requires the Member
#    session (owner), not the API Key client (client) -- see module docstring.
owner.accounts.authorize_application(organization_id, seller_account_id, application_id)
owner.accounts.authorize_application(organization_id, buyer_account_id, application_id)
owner.accounts.authorize_application(organization_id, marketplace_revenue_account_id, application_id)
print("[5] all three accounts authorized for the application")

# 6. Register where each SelfCustody beneficiary actually gets paid, and who pays for network
#    execution. The seller's destination is their OWN external wallet (a throwaway wallet here
#    stands in for "whatever wallet the seller really uses" -- Ishtaran never touches its key).
#    The marketplace's own commission lands on an address of its OWN execution wallet -- and that
#    same commission Account is the one registered to pay real network cost, out of its own
#    commission, a real business decision.
seller_wallet = generate_wallet()
seller_destination_address = derive_tron_address(seller_wallet.wallet.account_extended_public_key, 0)
client.execution_destinations.register(organization_id, seller_account_id, asset_network_id, seller_destination_address)
marketplace_revenue_allocation = client.wallets.allocate_deposit_address(application_id, network_id)
client.execution_destinations.register(organization_id, marketplace_revenue_account_id, asset_network_id, marketplace_revenue_allocation.address)
client.network_cost_payer_accounts.register(organization_id, asset_network_id, marketplace_revenue_account_id)
print("[6] ExecutionDestinations + NetworkCostPayerAccount registered")

# 7. Transaction + Payment Intent. An explicit Split is required here (2 non-payer Participants
#    -- seller and marketplace -- BR-SPL-004/BR-SPL-003: a single implicit 100% only applies with
#    exactly one beneficiary).
payer = ParticipantInput(account_id=buyer_account_id, role="payer", is_payer=True, split_percentage=None)
seller = ParticipantInput(account_id=seller_account_id, role="seller", is_payer=False, split_percentage=Decimal("90"))
marketplace = ParticipantInput(account_id=marketplace_revenue_account_id, role="marketplace", is_payer=False, split_percentage=Decimal("10"))
txn = client.transactions.create(organization_id, application_id, None, asset_network_id, Decimal("1000"), [payer, seller, marketplace], f"marketplace-txn-{t}")
intent = client.deposits.create_payment_intent(organization_id, txn.transaction_id, asset_network_id, Decimal("1000"))
full_intent = client.deposits.get_payment_intent(intent.payment_intent_id)
print("[7] payment_intent_id=", intent.payment_intent_id, "deposit_address=", full_intent.deposit_address)

# 8. Simulate the buyer's on-chain deposit and its confirmation (Sandbox only). Once confirmed,
#    the Transaction moves itself to RESERVED -- no explicit reserve() call.
observed = client.sandbox.simulate_deposit(environment_id, full_intent.deposit_address, asset_network_id, Decimal("1000"))
client.sandbox.simulate_confirmation(environment_id, observed.sandbox_observed_address_id, 1, True)
status = TransactionStatus.CREATED
for _ in range(20):
    if status not in (TransactionStatus.CREATED, TransactionStatus.AWAITING_FUNDS):
        break
    time.sleep(1)
    status = client.transactions.get_state(txn.transaction_id).status
print("[8] deposit confirmed, transaction status=", status.name)

# 9. Settlement -- calculates the Platform Fee/Split AND builds a real SigningRequest itself
#    (SelfCustody, confirmed live): one ExecutionLeg per beneficiary (seller, marketplace
#    commission), each addressed via the ExecutionDestination registered in step 6. Nothing is
#    final yet -- signing_request_id is populated, but no Ledger Entry exists until every leg
#    confirms (step 10-11).
executed = client.settlements.execute_settlement(txn.transaction_id)
settlement = client.settlements.get(executed.settlement_id)
print("[9] settlement executed id=", settlement.settlement_id, "signing_request_id=", settlement.signing_request_id)

# 10. Sign every leg of THAT SAME SigningRequest, locally, with the marketplace's own execution
#     wallet -- the private key is used here and only here, never sent anywhere. A Settlement
#     with nothing to execute on-chain (every allocation Retained, Fee zero) has
#     signing_request_id=None; this example's Split always produces real legs to sign.
if settlement.signing_request_id is None:
    raise RuntimeError("Expected a real SigningRequest for this Settlement")
signing_request_id = settlement.signing_request_id
signing_request = client.signing_requests.get(signing_request_id)
for leg in signing_request.legs:
    hash_bytes = bytes.fromhex(leg.canonical_hash)
    signature = generated_wallet.signer.sign(signing_request.derivation_reference, hash_bytes)
    result = client.signing_requests.submit_signed_transaction(
        signing_request_id, leg.execution_leg_id, leg.canonical_hash, signature.hex().upper(),
    )
    print(f"[10] leg={leg.role} verified={result.verified} all_legs_verified={result.all_legs_verified}")

# 11. Simulate each leg's on-chain confirmation (Sandbox only) and wait for the Settlement to
#     reach Completed -- only then does the Ledger reflect anything (Delivered, never Available,
#     since both beneficiaries' ExecutionDestinations are external wallets -- see
#     concepts/self-custody and concepts/transactions-settlements on the docs site).
for _ in range(20):
    current = client.signing_requests.get(signing_request_id)
    all_referenced = all(leg.broadcast_reference for leg in current.legs)
    if all_referenced:
        for leg in current.legs:
            broadcast_attempt_id = sandbox_broadcast_attempt_id_from_reference(leg.broadcast_reference)
            client.sandbox.simulate_broadcast_confirmation(environment_id, broadcast_attempt_id, 1, True)
        break
    time.sleep(0.5)

final_settlement = client.settlements.get(settlement.settlement_id)
for _ in range(30):
    if final_settlement.status.name == "COMPLETED":
        break
    time.sleep(0.5)
    final_settlement = client.settlements.get(settlement.settlement_id)
print("[11] settlement status=", final_settlement.status.name)

seller_payable = client.payout.get_payable_summary(seller_account_id, asset_network_id)
marketplace_payable = client.payout.get_payable_summary(marketplace_revenue_account_id, asset_network_id)
print("[11] seller paid=", seller_payable.paid, "marketplace paid=", marketplace_payable.paid)
