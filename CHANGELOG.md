# Changelog

Follows [SemVer](https://semver.org/). This is a **Development Preview** — 0.x versions may
still change before a stable 1.0.0.

## [0.1.2] — 2026-08-25

- Fixed a real bug, found while building example 14: `AuthResource.sign_up(...)` never sent the
  `Idempotency-Key` header `POST /v1/auth/signup` requires — every real call failed with `400
  IDEMPOTENCY_KEY_REQUIRED`. Self-service onboarding via this SDK never actually worked before
  this fix. `sign_up` now takes an optional `idempotency_key` parameter, auto-generated when
  omitted, same convention as `OrganizationsResource.create`. No breaking change.
- Added `examples/14_marketplace_journey.py`: a full marketplace payment, verified live against
  the real Sandbox (self-service signup, a self-custody execution wallet, a seller
  `AccountHolder`, a buyer Payment Intent, and a locally signed payout) -- connects several
  existing examples into one closed cycle.
- `CORE_API.md` corrected: documents `account_holders`/self-custody resources it omitted, notes
  that `accounts.authorize_application`/`freeze`/`unfreeze`/`close`/`revoke_relationship` reject
  an API Key and require a Member session (found live, undocumented until now), and that a
  Transaction reserves itself automatically once its deposit is confirmed -- no `reserve()` call
  needed or valid in that path.
- `auth_resource.py` docstrings translated to English -- two Portuguese comments had slipped
  through the SDK's English-only cleanup.

## [0.1.1] — 2026-08-25

- `Environment.SANDBOX` now resolves to the real public Sandbox (`https://sandbox-api.ishtaran.com`,
  the canonical domain live since 2026-08-25 — Cloud Run Domain Mapping) by default — no explicit
  `base_url` needed, though one always overrides it. Previously it required an explicit `base_url`
  and raised `ValueError` otherwise. `Environment.PRODUCTION` is unchanged (still requires an
  explicit `base_url`). Backward compatible.
- Fixed: `SDK_VERSION` (sent as `ishtaran-python/<version>` on every request) was still hardcoded
  to the pre-release placeholder `1.0.0.dev0`, misreporting the actual published version. Now
  `0.1.1`, matching `pyproject.toml`.

## [0.1.0] — 2026-08-24

First public release, published on PyPI (`pip install ishtaran`). Builds on the `1.0.0.dev0`
work below, plus:

### Added since `1.0.0.dev0`

- Self-custody wallet generation and restoration (`ishtaran.wallet.generate`/`restore`,
  BIP39/BIP32/BIP44).
- Tron address derivation from the public account key only (`derive_tron_address`).
- Local canonical-hash signing (reference `Signer`), documented as unsafe for Production —
  implement your own against a Vault/KMS/HSM for any real deployment.
- `client.wallets`/`client.signing_requests` — the real `ExecutionCustody` HTTP routes end to end.
- `client.account_holders` — self-service for the financial holder's global identity.
- License: Apache License 2.0.

### Known, still pending

- Production blockchain execution is not available yet.

## [1.0.0.dev0] — 2026-08-17

Third implementation of the Ishtaran Official SDK Program — 100% functional parity with the
Java SDK (reference implementation).

### Added

- Central client (`IshtaranClient.create(...)`).
- Complete Core API — 16 modules, 93 real operations.
- Easy Mode — `receive_payment`/`get_payment`/`wait_for_payment`, `withdraw`, `get_balance`,
  `verify_webhook_signature`.
- `X-Api-Key` + Member JWT authentication.
- Complete `IshtaranError` hierarchy.
- Safe retry with backoff+jitter.
- Idempotency (body and header, depending on the endpoint).
- Real pagination via lazy generators.
- Forward-compatible enums (`from_raw`/`is_unknown`, `UNKNOWN` fallback).
- Money always as `decimal.Decimal` (never `float`), via `json.loads(parse_float=Decimal,
  parse_int=Decimal)`.
- `verify_webhook_signature`/`compute_webhook_signature` (HMAC-SHA256, constant time).
- Opt-in logging with central redaction.
- HTTP redirects never followed automatically (`follow_redirects=False`).
- `mypy --strict` clean across all 63 modules of the SDK.
- Packaging validated — real wheel + sdist (`python -m build`), installed in a clean venv.

### Known, still pending

- Sync only in this version (`httpx.Client`) — async support is a documented future extension,
  same pacing allowed for Java ("sync-first initially").
- Real PyPI publication — blocked on a pending licensing decision.
