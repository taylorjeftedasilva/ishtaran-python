# Ishtaran Python SDK

Official Python SDK for the [Ishtaran API](https://ishtaran.com) — a programmable financial
platform (virtual accounts, conditional release workflows, settlements, and self-custody
blockchain execution).

**Public Sandbox available · Production not yet available**

## Project status

Ishtaran's public Sandbox is live and has been validated end to end (signup → payment →
self-custody signing → simulated broadcast → reconciliation), with all four official SDKs
published on their real package registries.

- **Public Sandbox:** available now, simulated blockchain execution, no real funds involved.
- **Production blockchain execution is not available yet** — no real blockchain connector is
  registered; see [Production status](#production-status) below.

See [Sandbox](#sandbox) below for how to point this SDK at it.

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

### Execution destinations (required before a SelfCustody `Settlement` can execute)

`client.execution_destinations.register` declares the real on-chain address a beneficiary
`Account` receives funds at, for a given `AssetNetwork`. `settlements.execute_settlement` now
resolves the destination for every beneficiary (and for the Platform Fee) before it builds a
`SigningRequest` — if none is registered, the call fails fast with a clear error before any
signing/broadcast starts, rather than silently reusing a withdrawal destination or guessing.
First-registration-wins: a second call for the same `account_id`+`asset_network_id` pair is
rejected, never silently overwritten.

```python
destination = client.execution_destinations.register(organization_id, seller_account_id, asset_network_id, seller_address)
```

Once a `Settlement` moves to SelfCustody execution, `SettlementResponse.signing_request_id` is
populated — fetch it with `client.signing_requests.get(signing_request_id)` to sign locally, the
same flow as above.

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
  validation, local signing, signed transaction submission, execution destination registration

This is deliberately not a full reference — see [FEATURES.md](FEATURES.md) and the
[API Reference](https://ishtaran.com/docs/api/ishtaran-api) for details.

## Installation

```bash
pip install ishtaran
```

`0.1.0` is a real, published **Development Preview** release on PyPI -- verified live with a
real `pip install` from a clean environment. See [CHANGELOG.md](CHANGELOG.md) for what's in it.

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
    environment=Environment.SANDBOX,  # resolves to the real public Sandbox; LOCAL/PRODUCTION also available
)

balance = client.get_balance(account_id, asset_network_id)
print("Available:", balance.available)  # decimal.Decimal, never float
```

See [`GETTING_STARTED.md`](GETTING_STARTED.md) and [`examples/`](examples/).

## Sandbox

The public Sandbox is live at `https://sandbox-api.ishtaran.com`
(`Environment.SANDBOX` resolves to it automatically -- no `base_url` needed, though an explicit
`base_url` always overrides it). The raw Cloud Run URL from the initial 2026-08-24 deploy still
works, but is no longer advertised -- use the canonical domain above.

- Sandbox uses simulated blockchain execution — no real funds are involved.
- The self-custody signing protocol described above is fully exercised in Sandbox: signatures
  are not skipped just because execution is simulated.
- Rate limits and idempotency behave the same as Production; only the blockchain broadcast is
  simulated.

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

`0.1.0` (Development Preview) is published on PyPI -- see [Installation](#installation). Future
releases follow the same path: a reviewed, tested commit gets a new semver tag, and PyPI
Trusted Publishing (OIDC, no long-lived token) publishes it automatically.

## License

This SDK is licensed under the Apache License 2.0. See [LICENSE](LICENSE).
