# Changelog

Follows [SemVer](https://semver.org/). This is a **Development Preview** — 0.x versions may
still change before a stable 1.0.0.

## [0.1.2] — 2026-08-29

- Added `client.execution_destinations.register(organization_id, account_id, asset_network_id,
  address)` (`POST /v1/organizations/{organization_id}/execution-destinations`) -- registers the
  real on-chain address a beneficiary `Account` receives funds at, for a given `AssetNetwork`.
  Required before a `Settlement` involving that Account can execute under SelfCustody (`DEC-037`):
  `settlements.execute_settlement` now resolves every beneficiary's (and the Platform Fee's)
  destination before building a `SigningRequest` and fails fast, before any signing/broadcast, if
  none is registered. First-registration-wins -- a second call for the same `account_id`+
  `asset_network_id` is rejected, never silently overwritten. Also added
  `SettlementResponse.signing_request_id` -- populated once a `Settlement` moves to SelfCustody
  execution; fetch it with `client.signing_requests.get(signing_request_id)` to sign locally.
  Found and fixed while closing out the real on-chain execution path for the Mercatto Business
  Case -- the backend's `ISettlementExecutionStrategy` split
  (`SelfCustodySettlementExecutionStrategy` vs. legacy `ManagedCustodySettlementExecutionStrategy`)
  was already implemented, but no SDK exposed the new `ExecutionDestination` resource or the
  `signing_request_id` needed to actually complete a real Settlement end to end. No breaking
  change -- both are additive.
- **Breaking (positional args):** `SettlementsResource.execute_settlement(transaction_id, idempotency_key=None)`
  is now `execute_settlement(transaction_id, amount=None, idempotency_key=None)` -- a new `amount`
  parameter was inserted before `idempotency_key`. Callers using `idempotency_key` as a keyword
  argument are unaffected; a caller passing it positionally as the 2nd argument needs to move it
  to the 3rd, or switch to the keyword form. Enables Partial Settlement (`BL-STL-008`, activated
  2026-08-26): `amount=None` settles the full remaining reserved amount (unchanged default), or
  pass a `Decimal` to settle exactly that amount -- callable multiple times on the same Transaction
  until the remaining balance reaches zero, each call computing its own Platform Fee on its own
  gross slice. Found and fixed while building the Mercatto marketplace Business Case: the
  platform's domain/Application layer already supported this per-call `Amount` since `DEC-019`,
  but the HTTP contract never exposed it -- a real, deliberate MVP deferral (`BL-STL-008`,
  Pós-MVP) now activated by explicit product decision.
- Fixed a real bug in the platform's Ledger module, also found via the Mercatto Business Case:
  `BR-BAL-005` (Asset Network `MinAmount`/`MaxAmount`) was being enforced on every individual
  Ledger Entry of every internal record command -- including Settlement's Fee/Split postings --
  instead of only on the Gross Amount of a Reserve/Release operation, as the platform's own Ledger
  spec always documented. No SDK-visible API change -- documented here because it directly affects
  which amounts a real `execute_settlement()` call can now succeed with.

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
