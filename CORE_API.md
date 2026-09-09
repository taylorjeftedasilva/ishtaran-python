# Core API

Complete, literal coverage of the real API — 100 routes, 16 modules (see `SDK_FEATURE_MATRIX.md`,
`SDK_METHOD_MAP.md`). No invented endpoint, no admin-only/platform-only route exposed.

## Control Plane (always Member JWT)

`client.organizations`, `client.applications`, `client.environments`, `client.api_keys`,
`client.members`, `client.asset_network_catalog`, `client.webhook_endpoints`, `client.webhook_deliveries`.

## Data Plane (API Key or Member JWT)

`client.accounts`, `client.transactions`, `client.deposits`, `client.ledger`, `client.settlements`,
`client.refunds`, `client.withdrawals`, `client.workflows`/`event_types`/`events`, `client.sandbox`.

**Except:** `accounts.authorize_application`/`freeze`/`unfreeze`/`close`/`revoke_relationship`
reject an API Key and require a Member session (verified live, not documented anywhere else --
`MemberPermissionPolicy.Require`, `AccountsEndpoints.cs`).

## AccountHolders (isolated session, own auth)

`client.account_holders` — the financial holder's global identity (`DEC-032`): `sign_up`/`login`/
`me`/`claim_invitation`/`sign_up_and_claim_invitation`. Its session token is never shared with
`client.auth` (Member) nor with the Organization's `X-Api-Key` on the same client instance — treat
it as a third, independent authentication context. See [README.md § Self-custody /
AccountHolders](README.md#what-this-sdk-does) for the identity model.

## Self-custody (`ExecutionCustody`)

`client.wallets` / `client.signing_requests` — wallet registration, deposit address allocation,
`SigningRequest` creation/submission. `client.execution_destinations` — registers the real
on-chain address a beneficiary `Account` gets paid at for a given `AssetNetwork`; required before a
`Settlement` can execute under SelfCustody (`DEC-037`) — `settlements.execute_settlement` fails
fast, before any signing/broadcast, if a participant has none registered. Covered with a full
worked example in [README.md § Self-custody](README.md#self-custody) rather than duplicated here —
the interesting part of this module is the local signing flow, not the HTTP resource shape.

## Network Execution Engine (`ExecutionCustody`)

`client.network_execution.quote(environment_id, asset_network_id, operations, network_cost_payer)`
prices a plan of 1..N physical on-chain operations (`SPEC-NETEXEC-001`). It is a **preview only** —
it never writes anything, and Settlement/Withdrawal/Payout each get/re-get their own quote
internally at execution time (`preview quote != execution quote`, never reuse this response as a
price guarantee). The response's `total_charged` (in `quote_currency`) is what gets debited;
`native_execution_cost`/`authorized_native_cost` are always in the resource asset's native units;
`margin` is the Ishtaran markup applied in `ISHTARAN_RESOURCES` mode (always `"0"` in
`CUSTOMER_RESOURCES` mode).

Two registrations gate which mode an Organization actually runs in for a given `AssetNetwork`:

- `client.execution_sources.register(...)` registers the address `ExecutionCustody` signs FROM to
  pay network cost; `client.execution_sources.sync_resource_stake(organization_id,
  execution_source_id, available_native_amount, available_energy, available_bandwidth)` is the
  self-reported (no on-chain verification in this version) declaration of that address's
  available on-chain resource capacity — required before `CUSTOMER_RESOURCES` (`SELF`) mode can
  ever succeed for it, and safe to call again any time to re-sync (no first-registration-wins
  restriction, unlike `register`).
- `client.network_cost_payer_accounts.register(organization_id, asset_network_id, account_id)`
  registers the Account debited for the *charged* cost (first-registration-wins per
  `(organization_id, asset_network_id)`); `client.network_cost_payer_accounts.update_resource_preference(
  organization_id, asset_network_id, resource_preference, allow_fallback_to_ishtaran_resources)`
  switches that Organization's Network Execution mode for the `AssetNetwork` between `SELF`
  (`CUSTOMER_RESOURCES`, the integrator's own on-chain resources) and `ISHTARAN_SPONSORED` (the
  default). `allow_fallback_to_ishtaran_resources` only matters when `resource_preference` is
  `SELF` — it decides whether an insufficient `CUSTOMER_RESOURCES` balance falls back to
  `ISHTARAN_RESOURCES` instead of failing closed. Requires a `NetworkCostPayerAccount` already
  registered via `register` first.

## Withdrawal

- `client.withdrawals.quote(organization_id, environment_id, account_id,
  withdrawal_destination_id, asset_network_id, amount)` — a pure read, never writes anything; the
  response always exposes `estimated_network_fee`/`estimated_recipient_amount`, never hiding the
  network cost.
- `client.withdrawals.request(...)` — the same arguments plus an idempotency key; builds the real
  Withdrawal and, under SelfCustody, its `SigningRequest` (singular field only — Withdrawal never
  supports multi-source funding the way Settlement does, see
  [CORE_API.md § Self-custody](#self-custody-executioncustody)).
- **Destination cooldown**: a newly-registered `WithdrawalDestination` can't be withdrawn to for
  **24 hours by default** (`WithdrawalPolicy.cooldown_hours`, platform-enforced floor of 1 hour —
  an Organization can raise it, never lower it below the floor). Adding a *new* destination when
  an active one already exists for the same AssetNetwork (an account-takeover pattern) uses a
  separate, longer cooldown — **7 days by default** (`destination_change_cooldown_hours`). Neither
  cooldown has a bypass — never build a flow that assumes one.
- **Reconciliation**: a Withdrawal whose broadcast can't be automatically resolved moves to a
  terminal status the backend calls `RequiresReconciliation` (raw value `11`) rather than silently
  failing or retrying forever — surface it to a human, it needs manual platform-side resolution.
  **Known SDK gap, verified against the real backend enum**: this SDK's `WithdrawalStatus` only
  defines raw values `0`-`9` — status `11` (and `Failed`, `10`) come back as the forward-compatible
  unknown-value fallback rather than a named constant. Check the raw integer (`11`) if you need to
  detect this specific status today; treating any unrecognized/unknown status defensively (not
  just this one) is good practice regardless.
- `client.withdrawals.list`/`.list_all` — one of only 2 endpoints with real pagination (see
  § Real pagination below).

## Payout (`SPEC-024`/`SPEC-025`)

Payout is where Settlement's economic outcome (who owes what) turns into an actual delivery.
**Settlement != Payout**: `client.settlements.execute_settlement` records the economic truth
(obligations, splits, the Platform Fee) — it never itself moves a beneficiary's money on-chain.
Whether that delivery happens immediately or later depends on the Organization's `PayoutPolicy`:

- **`IMMEDIATE`** — a beneficiary's Payable is delivered the same moment as the Settlement itself;
  no `PayoutBatch` involved.
- **`MANUAL`** — the beneficiary only accrues an economic obligation until someone explicitly
  creates a `PayoutBatch` for them via `client.payout.create_batch(...)`.

These are the two `PayoutPolicy` modes with real public support today. The backend domain model
also defines `THRESHOLD` and `SCHEDULED` values, but neither has a public trigger yet (both are
rejected — no scheduler/threshold-crossing worker exists in this slice) — don't build against
them as available capabilities.

- `client.payout.get_payable_summary(account_id, asset_network_id)` — returns a
  `PayableSummaryResponse(accrued, reserved_for_payout, paid)` for that Account/AssetNetwork pair.
  **`accrued` is an economic obligation the platform owes that Account, never the same thing as
  the Account's own on-chain `available` balance** (from `client.get_balance`) — an Account can
  have a large `accrued` Payable and `0` available balance simultaneously (nothing paid out yet),
  or vice versa. `reserved_for_payout` is currently always `0` (no batch-scoped reservation exists
  yet).
- `client.payout.create_batch(organization_id, environment_id, asset_network_id,
  explicit_owner_ids, idempotency_key=None)` — creates a `PayoutBatch` covering the given
  beneficiaries' currently-accrued obligations. This SDK slice only ever sends `trigger = MANUAL`
  (the only trigger the public route accepts). Returns a `None` `payout_batch_id` (204, a
  legitimate no-op) when none of the given owners had an eligible obligation.
- `client.payout.get_batch(organization_id, payout_batch_id)` — full batch state: `status`,
  per-beneficiary `obligations` (each with its own `source_obligations`/`destination_address`/
  `status`), the frozen `network_execution_quote_snapshot` if network execution was involved, and
  a single `signing_request_id` (a PayoutBatch's own SelfCustody signing is not multi-source the
  way Settlement's is — see [CORE_API.md § Self-custody](#self-custody-executioncustody)).

## Example — full flow without Easy Mode

```python
from decimal import Decimal

account = client.accounts.create(organization_id, "customer-123")
# authorize_application requires the Member client (`member_client`), never the API Key one --
# see the note above.
member_client.accounts.authorize_application(organization_id, account.account_id, application_id)

txn = client.transactions.create(organization_id, application_id, None, asset_network_id, Decimal("100"), [payer, recipient])
intent = client.deposits.create_payment_intent(organization_id, txn.transaction_id, asset_network_id, Decimal("100"))
full_intent = client.deposits.get_payment_intent(intent.payment_intent_id)
# full_intent.deposit_address -- real address to watch on-chain

# Once the deposit is confirmed, the Transaction reserves itself -- no explicit reserve() call
# needed or valid in this path (verified live -- calling it here raises BR-TXN-002).
settlement = client.settlements.execute_settlement(txn.transaction_id)
```

See [`examples/14_marketplace_journey.py`](examples/14_marketplace_journey.py) for this same flow
run in full, including the Payment Intent → deposit → confirmation → self-custody payout signing
this snippet omits.

## Real anonymous objects

Several real POSTs return a minimal object (`CreateAccountResult(account_id=...)`,
`CreateTransactionResult(transaction_id=...)`) instead of the full resource — confirmed in the
real handler source code. Fetch the full resource with the corresponding `get(...)`.

## Real pagination (lazy generators)

Only 2 endpoints have real pagination: `withdrawals.list`/`.list_all` and
`ledger.list_entries`/`.list_all_entries`. The `.list_all*` variants are generators — they fetch
the next page on demand:

```python
for withdrawal in client.withdrawals.list_all(organization_id, page_size=20):
    print(withdrawal.withdrawal_id)
```
