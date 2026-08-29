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
