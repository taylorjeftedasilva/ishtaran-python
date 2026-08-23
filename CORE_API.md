# Core API

Complete, literal coverage of the real API — 83 routes, 16 modules (see `SDK_FEATURE_MATRIX.md`,
`SDK_METHOD_MAP.md`). No invented endpoint, no admin-only/platform-only route exposed.

## Control Plane (always Member JWT)

`client.organizations`, `client.applications`, `client.environments`, `client.api_keys`,
`client.members`, `client.asset_network_catalog`, `client.webhook_endpoints`, `client.webhook_deliveries`.

## Data Plane (API Key or Member JWT)

`client.accounts`, `client.transactions`, `client.deposits`, `client.ledger`, `client.settlements`,
`client.refunds`, `client.withdrawals`, `client.workflows`/`event_types`/`events`, `client.sandbox`.

## Example — full flow without Easy Mode

```python
from decimal import Decimal

account = client.accounts.create(organization_id, "customer-123")
client.accounts.authorize_application(account.account_id, application_id)

txn = client.transactions.create(organization_id, application_id, None, asset_network_id, Decimal("100"), [payer, recipient])
intent = client.deposits.create_payment_intent(organization_id, txn.transaction_id, asset_network_id, Decimal("100"))
full_intent = client.deposits.get_payment_intent(intent.payment_intent_id)
# full_intent.deposit_address -- real address to watch on-chain

settlement = client.settlements.execute_settlement(txn.transaction_id)
```

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
