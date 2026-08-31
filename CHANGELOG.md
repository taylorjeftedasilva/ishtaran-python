# Changelog

Follows [SemVer](https://semver.org/). This is a **Development Preview** — 0.x versions may
still change before a stable 1.0.0.

## [0.1.3] — 2026-08-31

- Added the Network Execution Engine and Payout surfaces (`SPEC-NETEXEC-001/002`, `SPEC-024/025`),
  found and validated live against the real Sandbox while rewriting the full marketplace journey
  example (`examples/14_marketplace_journey.py`):
  - `client.network_execution.quote(...)` — a fresh, per-broadcast quote of the real network
    resources (e.g. TRON Energy/Bandwidth) an execution will consume, always independent of the
    Platform Fee.
  - `client.execution_sources.register(...)` — registers the wallet/address that actually pays
    for a batched `PayoutBatch`'s own broadcast (distinct from `NetworkCostPayerAccount` below —
    needed for `Withdrawal` execution and `PayoutBatch` creation, never for a Settlement's
    Immediate path).
  - `client.network_cost_payer_accounts.register(organization_id, asset_network_id, account_id)`
    — registers which of the Organization's own Accounts is debited for the real network
    execution cost of every SelfCustody Settlement/Withdrawal/PayoutBatch on a given AssetNetwork.
    **Required before the first real Settlement with anything to pay out** — without it,
    `execute_settlement()` fails with 422 `PAYOUT_BATCH_NETWORK_COST_PAYER_ACCOUNT_NOT_REGISTERED`,
    before it builds any `SigningRequest`.
  - `client.payout.get_payable_summary(account_id, asset_network_id)` — reads a beneficiary's
    `accrued`/`reserved_for_payout`/`paid` amounts. Under SelfCustody with an external-wallet
    `ExecutionDestination`, a beneficiary's `available` Ledger balance legitimately stays `0`
    forever — `paid` (`Delivered`) is the real "have they been paid" signal.
  - `client.payout.create_batch(...)`/`get_batch(...)` — this SDK slice only ever creates batches
    with `trigger = MANUAL`; `THRESHOLD_CROSSED`/`SCHEDULED` exist in the domain model but have no
    public route to trigger them yet.
  - `SettlementResponse.signing_request_ids` (plural, `SPEC-ADDRESSPOOL-001`) — one entry per
    physical funding source frozen for a Settlement; `signing_request_id` remains a compatibility
    field, always the first entry.
  - `WithdrawalResponse`/`WithdrawalQuoteResponse` gained `environment_id`, `signing_request_id`,
    `network_execution_cost`, `network_execution_cost_status`. `estimated_network_fee`/
    `final_network_fee` are now deprecated and nullable — always `None` under SelfCustody;
    `network_execution_cost` is the real source of truth.
  All additive, no breaking change from these alone.
- **Breaking (real bug fix, not a redesign):** `withdrawals_resource.quote(...)`/`.request(...)`
  now take `environment_id` as an inserted positional parameter
  (`organization_id, environment_id, account_id, withdrawal_destination_id, asset_network_id,
  amount, idempotency_key=None`). The backend has required `EnvironmentId`
  (`RequestWithdrawalRequest.cs`/`WithdrawalQuoteRequest.cs`) since a prior session's SelfCustody
  migration (commit `408ac5e`) — this SDK never sent it. Every real `withdrawals.request()` call
  through this SDK would have failed with 400 `VALIDATION_ERROR` before this fix; confirmed live
  against a real backend, not just inferred. Any caller must add the new argument.
- Rewrote `examples/14_marketplace_journey.py`: `execute_settlement()` now builds its own
  `SigningRequest` automatically (confirmed live) — the previous version manually called
  `signing_requests.create()` with hand-picked addresses right after `execute_settlement()`, which
  built a second, disconnected `SigningRequest`. The example now registers a
  `NetworkCostPayerAccount` and per-beneficiary `ExecutionDestination`s, uses a real 2-beneficiary
  explicit Split, and signs the real `settlement.signing_request_id`.
- Note for cross-SDK parity: unlike the TypeScript SDK, `transactions.create(...)`/
  `receive_payment(...)` in this SDK still have no `environment_id` parameter at all — a known,
  tracked gap, not fixed in this release (the backend doesn't hard-reject its absence here, unlike
  for Withdrawals above). See `SDK_CAPABILITY_SPEC.md` item 10.

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
