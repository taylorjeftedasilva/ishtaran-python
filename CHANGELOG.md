# Changelog

Follows [SemVer](https://semver.org/). This is a **Development Preview** — 0.x versions may
still change before a stable 1.0.0.

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

- The public Sandbox is not live yet.
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
