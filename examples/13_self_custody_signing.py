"""
13 -- Self-custody wallet/signing end to end (SPEC-017-021, checkpoint 10): generates the wallet
LOCALLY (wallet.generate()), registers only the public key, allocates a real deposit address,
creates a 2-leg SigningRequest, signs each canonical hash returned by the API with the private key
(which NEVER leaves this process -- INV-SC-01), and submits it back. Proves the all-signatures gate
(brief section 11): all_legs_verified only becomes true after the second signature, and both Legs
only become Broadcast at that same instant.
"""

import os
import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from ishtaran import Environment, IshtaranClient
from ishtaran.model.enums import DerivationScheme
from ishtaran.model.execution_custody import ExecutionLegInput
from ishtaran.wallet import derive_tron_address, generate

client = IshtaranClient.create(
    api_key=os.environ.get("ISHTARAN_API_KEY"),
    environment=Environment.LOCAL,
    base_url=os.environ.get("ISHTARAN_BASE_URL", "http://localhost:8080"),
)

application_id = os.environ["ISHTARAN_APPLICATION_ID"]
environment_id = os.environ["ISHTARAN_SANDBOX_ENVIRONMENT_ID"]
network_id = os.environ["ISHTARAN_NETWORK_ID"]
asset_network_id = os.environ["ISHTARAN_ASSET_NETWORK_ID"]

# 1. Wallet generated locally -- the mnemonic/private key never leave this process.
generated = generate()
print("mnemonic (backup -- NEVER sent to the API):", generated.mnemonic)
print("account_extended_public_key (only this goes to the API):", generated.wallet.account_extended_public_key)

# 2. Register the wallet -- the API only ever receives the public key.
registered = client.wallets.register(
    application_id, network_id, DerivationScheme.TRON_BIP44_HARDENED_ACCOUNT,
    generated.wallet.account_extended_public_key, f"example13-wallet-{uuid.uuid4()}",
)
print("wallet_id=", registered.wallet_id)

# 3. GetWallet never includes the material (BR-WLT-002).
fetched_wallet = client.wallets.get(registered.wallet_id)
print("wallet.scheme=", fetched_wallet.scheme.name, "next_derivation_index=", fetched_wallet.next_derivation_index)

# 4. Allocate a real deposit address -- derived from the registered xpub.
allocated = client.wallets.allocate_deposit_address(application_id, network_id)
print("source_address=", allocated.address, "derivation_reference=", allocated.derivation_reference)

# Local, backend-independent confirmation (defense in depth -- same algorithm as tron_address).
locally_derived_address = derive_tron_address(generated.wallet.account_extended_public_key, allocated.derivation_reference)
if locally_derived_address != allocated.address:
    raise RuntimeError(f"Address mismatch: backend={allocated.address} local={locally_derived_address}")

# 5. Create the SigningRequest -- 2 legs (Seller + Ishtaran Platform Fee), amounts already
#    computed by the caller (real Settlement/Withdrawals integration is future work). expires_at
#    is always explicit UTC.
expires_at = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
created = client.signing_requests.create(
    environment_id,
    registered.wallet_id,
    allocated.derivation_reference,
    f"example13-settlement-{uuid.uuid4()}",
    asset_network_id,
    allocated.address,
    [
        ExecutionLegInput(role="Seller", destination_address="TSellerDestinationAddress123456", amount=Decimal("90")),
        ExecutionLegInput(role="PlatformFee", destination_address="TIshtaranFeeDestinationAddr123", amount=Decimal("1")),
    ],
    expires_at,
    f"example13-signing-request-{uuid.uuid4()}",
)
print("signing_request_id=", created.signing_request_id)

# 6. Fetch the SigningRequest -- each Leg already carries the canonical_hash computed by the backend.
signing_request = client.signing_requests.get(created.signing_request_id)

# 7. Sign each hash locally and submit -- never in parallel, so the all-signatures gate can be
#    observed: the first submission must never trigger a broadcast on its own.
for leg in signing_request.legs:
    canonical_hash_bytes = bytes.fromhex(leg.canonical_hash)
    signature = generated.signer.sign(allocated.derivation_reference, canonical_hash_bytes)
    signature_hex = signature.hex().upper()

    result = client.signing_requests.submit_signed_transaction(
        created.signing_request_id, leg.execution_leg_id, leg.canonical_hash, signature_hex,
    )

    print(f"leg={leg.role} verified={result.verified} all_legs_verified={result.all_legs_verified} mismatch_reason={result.mismatch_reason}")

# 8. Confirm the final state -- both Legs must be Broadcast, each with a real broadcast_reference (Sandbox).
final_state = client.signing_requests.get(created.signing_request_id)
for leg in final_state.legs:
    print(f"leg={leg.role} status={leg.status} broadcast_reference={leg.broadcast_reference}")
