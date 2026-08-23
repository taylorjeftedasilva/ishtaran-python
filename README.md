# Ishtaran Python SDK

Official Python SDK for the [Ishtaran API](https://ishtaran.com) — a programmable financial
platform (virtual accounts, conditional release workflows, settlements, and self-custody
blockchain execution).

**Development Preview · Public Sandbox coming soon · Production not yet available**

## Project status

Ishtaran is currently under active development.

The official SDKs already include the current HTTP API capabilities and the self-custody
wallet/signing protocol, but the public Sandbox is still being prepared.

- **Public Sandbox target:** approximately two weeks from August 23, 2026. This is a planned,
  expected target, not a guarantee.
- **Production blockchain execution is not available yet.**

See [Sandbox](#sandbox) and [Production status](#production-status) below for what that means
concretely today.

## What this SDK does

Third implementation of the Ishtaran Official SDK Program
(Java → TypeScript → **Python** → Go), 100% functional parity with the Java SDK (reference
implementation). See also: [Java](https://github.com/taylorjeftedasilva/ishtaran-java) ·
[TypeScript/Node.js](https://github.com/taylorjeftedasilva/ishtaran-node) ·
[Go](https://github.com/taylorjeftedasilva/ishtaran-go).

Two layers over the same backend:

- **Easy Mode** — `client.receive_payment(...)`, `client.withdraw(...)`, `client.get_balance(...)`,
  `client.verify_webhook_signature(...)`: fast composition, never duplicates business logic.
- **Core API** — `client.accounts`, `client.transactions`, `client.withdrawals`, etc.: granular
  access to the same real API endpoints, with nothing invented beyond what the real API exposes.
- **AccountHolders** — `client.account_holders`: self-service for the financial holder's global
  identity — `sign_up`/`login`/`me`/`claim_invitation`/`sign_up_and_claim_invitation`.
  Isolated session: never shares a token with `client.auth` (Member) nor with the
  Organization's API Key within the same client instance.

## Self-custody

**Your keys stay with you. The SDK signs locally. Ishtaran verifies and relays. The blockchain
executes.**

- Wallet generation/restoration happens client-side, inside this SDK.
- Private keys, seeds, and mnemonic phrases never need to be sent to Ishtaran.
- Signing happens in your own environment/process.
- The SDK validates the signing context before signing.
- Ishtaran only ever receives public wallet/derivation material and signed execution payloads.
- Ishtaran verifies each signature, relays the transaction, and monitors and reconciles
  execution.
- Sandbox and Production use the same signing semantics from the SDK's perspective — environment
  behavior (simulated vs. real execution) is resolved by the Ishtaran API/infrastructure, never
  by a special cryptographic code path inside the SDK.

The `ishtaran.wallet` module generates or restores a BIP39/BIP32/BIP44 wallet locally and signs a
leg's canonical hash. **The private key, seed, and mnemonic never leave this code and are never
sent to Ishtaran.**

```python
from ishtaran.wallet import generate
from ishtaran.model.enums import DerivationScheme

# Wallet generated locally -- the mnemonic/private key never leave this process.
generated = generate()  # 24-word mnemonic, back it up now -- it is shown only once

# Only the public key is registered with Ishtaran.
registered = client.wallets.register(
    application_id, network_id, DerivationScheme.TRON_BIP44_HARDENED_ACCOUNT,
    generated.wallet.account_extended_public_key, idempotency_key,
)

# Signing also happens locally, against a hash Ishtaran computed and verifies.
signature = generated.signer.sign(0, canonical_hash)
```

`generated.signer` (the reference `Signer` returned by `generate()`) keeps the account private
key in plain process memory — **documented as unsafe for Production.** Implement the `Signer`
interface yourself against a Vault/KMS/HSM/OS keychain for any real deployment; the interface
never mandates a specific backend.

See [`examples/13_self_custody_signing.py`](examples/13_self_custody_signing.py) for the full
runnable flow (register a wallet, allocate a deposit address, create a `SigningRequest`, sign and
submit every leg), and [Self-Custody](https://ishtaran.com/docs/concepts/self-custody) for the
complete protocol detail.

## Current capabilities

- Organizations / Applications / Environments
- API Keys
- Accounts / AccountHolders
- Payment Intents / Deposits
- Ledger
- Transactions
- Workflows / Rules
- Settlements / Splits / Fees / Refunds
- Withdrawals
- Webhooks
- Self-custody: wallet generation/restore, public address derivation, `SigningRequest`
  validation, local signing, signed transaction submission

This is deliberately not a full reference — see [FEATURES.md](FEATURES.md) and the
[API Reference](https://ishtaran.com/docs/api/ishtaran-api) for details.

## Installation

Not yet published on PyPI — package registry distribution is planned alongside the public
Sandbox launch (see [Package distribution roadmap](#package-distribution-roadmap)). The source is
public today:

```bash
pip install git+https://github.com/taylorjeftedasilva/ishtaran-python.git
```

Or for local development:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

Requires **Python 3.10+**.

## Quick example

```python
from ishtaran import IshtaranClient, Environment

client = IshtaranClient.create(
    api_key=os.environ["ISHTARAN_API_KEY"],
    environment=Environment.LOCAL,  # or SANDBOX/PRODUCTION with an explicit base_url
)

balance = client.get_balance(account_id, asset_network_id)
print("Available:", balance.available)  # decimal.Decimal, never float
```

See [`GETTING_STARTED.md`](GETTING_STARTED.md) and [`examples/`](examples/).

## Sandbox

The public Sandbox is not live yet.

- **Planned target:** approximately two weeks from August 23, 2026.
- Sandbox uses simulated blockchain execution — no real funds are involved.
- The self-custody signing protocol described above is still fully exercised in Sandbox:
  signatures are not skipped just because execution is simulated.

This section will be updated with real onboarding steps when the public Sandbox launches.

## Production status

**Production blockchain execution is not available yet.**

Additional networks/assets may be mentioned elsewhere in this project as roadmap items — none of
them should be read as available in Production today.

## Security

- Never commit API keys.
- Never transmit mnemonic phrases, seeds, or private keys to Ishtaran — there is no legitimate
  reason for any Ishtaran API call to ever need them.
- Use a production-grade KeyStore/Signer implementation for real deployments.
- The reference in-memory `Signer` returned by `generate()` is an example, not a production
  secret-storage solution.
- Verify the expected destination, asset, amount, and signing context before signing.
- Treat any integration, tool, or request asking you to upload private key material as invalid.

See [SECURITY.md](SECURITY.md) for more detail.

## Documentation

| Document | Content |
|---|---|
| [GETTING_STARTED.md](GETTING_STARTED.md) | First use |
| [AUTHENTICATION.md](AUTHENTICATION.md) | `X-Api-Key` vs. Member JWT |
| [EASY_MODE.md](EASY_MODE.md) | When to use Easy Mode vs. Core |
| [CORE_API.md](CORE_API.md) | Complete resource coverage |
| [ERROR_HANDLING.md](ERROR_HANDLING.md) | `IshtaranError` hierarchy |
| [IDEMPOTENCY.md](IDEMPOTENCY.md) | Automatic vs. explicit key |
| [RETRIES.md](RETRIES.md) | Retry policy |
| [WEBHOOKS.md](WEBHOOKS.md) | Signature verification |
| [CONFIGURATION.md](CONFIGURATION.md) | Client configuration |
| [SECURITY.md](SECURITY.md) | Secrets, TLS, redaction |
| [FEATURES.md](FEATURES.md) | Capability coverage |
| [CHANGELOG.md](CHANGELOG.md) | Version history |

Every behavior is derived from the real API, never invented — see the
[Documentation](https://ishtaran.com/docs/intro) and [API Reference](https://ishtaran.com/docs/api/ishtaran-api).

## Money is always `Decimal`

Every monetary field is typed as `decimal.Decimal` — never `float`. The real API sends money as
`number(double)` in JSON; Python's standard parser (`float`) would already lose precision before
the SDK could intervene, so all response parsing uses `json.loads(text, parse_float=Decimal,
parse_int=Decimal)`, preserving the exact text of every number. See the
[API Reference](https://ishtaran.com/docs/api/ishtaran-api) for the real JSON shape of every
monetary field.

## A note on sync/async

This version is **synchronous** (`httpx.Client`) — the same pacing allowed for Java ("sync-first
initially") by the SDK Program brief. Async support (`httpx.AsyncClient`, `async`/`await` with
real API parity) remains a documented future extension, not a hidden limitation.

## Package distribution roadmap

Not yet published on a package registry. Alongside the public Sandbox launch, the plan is to
distribute this SDK through PyPI (`pip install ishtaran`). Until then, build/install directly
from this source repository — see [Installation](#installation) above.

## License

This SDK is licensed under the Apache License 2.0. See [LICENSE](LICENSE).
