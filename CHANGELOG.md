# Changelog

Follows [SemVer](https://semver.org/). Not yet published (PyPI).

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
