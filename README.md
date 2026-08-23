# Ishtaran Python SDK

Official Python SDK for the [Ishtaran API](https://ishtaran.com) — a programmable financial
platform. Third implementation of the Ishtaran Official SDK Program
(Java → TypeScript → **Python** → Go), 100% functional parity with the Java SDK (reference
implementation). See also: [Java](https://github.com/taylorjeftedasilva/ishtaran-java) ·
[TypeScript/Node.js](https://github.com/taylorjeftedasilva/ishtaran-node) ·
[Go](https://github.com/taylorjeftedasilva/ishtaran-go).

## Two layers, same backend

- **Easy Mode** — `client.receive_payment(...)`, `client.withdraw(...)`, `client.get_balance(...)`,
  `client.verify_webhook_signature(...)`: fast composition, never duplicates business logic.
- **Core API** — `client.accounts`, `client.transactions`, `client.withdrawals`, etc.: granular
  access to the same real API endpoints (see the
  [API Reference](https://ishtaran.com/docs/api/ishtaran-api) / [raw OpenAPI](https://ishtaran.com/openapi.json)).
- **AccountHolders** — `client.account_holders`: self-service for the financial holder's global
  identity (`DEC-032`) — `sign_up`/`login`/`me`/`claim_invitation`/`sign_up_and_claim_invitation`.
  Isolated session: never shares a token with `client.auth` (Member) nor with the
  Organization's API Key within the same client instance.

## Installation

Not yet published on PyPI (licensing decision pending), but the source is public:

```bash
pip install git+https://github.com/taylorjeftedasilva/ishtaran-python.git
```

Or for local development:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

Requires **Python 3.10+**.

## Quickstart

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

## Money is always `Decimal`

Every monetary field is typed as `decimal.Decimal` — never `float`. The real API sends money as
`number(double)` in JSON; Python's standard parser (`float`) would already lose precision before
the SDK could intervene, so all response parsing uses `json.loads(text, parse_float=Decimal,
parse_int=Decimal)`, preserving the exact text of every number. See the
[API Reference](https://ishtaran.com/docs/api/ishtaran-api) for the real JSON shape of every
monetary field.

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

## A note on sync/async

This version is **synchronous** (`httpx.Client`) — the same pacing allowed for Java ("sync-first
initially") by the SDK Program brief. Async support (`httpx.AsyncClient`, `async`/`await` with
real API parity) remains a documented future extension, not a hidden limitation.
