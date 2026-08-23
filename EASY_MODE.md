# Easy Mode vs. Core API

## Use Easy Mode when...

- You want to integrate fast: `client.receive_payment(...)`, `client.withdraw(...)`, `client.get_balance(...)`.
- You need to safely wait for an asynchronous result: `client.wait_for_payment(...)`,
  `client.withdrawals.wait_for(...)`, `client.transactions.wait_for(...)` — always with a timeout.
- You only need to verify a webhook signature: `client.verify_webhook_signature(...)`.

## Use Core API when...

- You need granular control (`client.transactions.reserve(...)` vs. `client.settlements.execute_settlement(...)`).
- You need a resource that Easy Mode doesn't cover — 93 real operations, see `SDK_FEATURE_MATRIX.md`.
- You want real pagination: `client.withdrawals.list_all(...)`/`client.ledger.list_all_entries(...)`
  (lazy generators) instead of a single call.

## Concrete equivalence

| Easy Mode | Core equivalent |
|---|---|
| `client.receive_payment(...)` | `transactions.create()` + `deposits.create_payment_intent()` + `deposits.get_payment_intent()` |
| `client.withdraw(...)` | `withdrawals.create_destination()` + `withdrawals.request()` |
| `client.get_balance(...)` | `ledger.get_balance(...)` |

Easy Mode never hides the real `withdrawal_id`/`transaction_id`/`payment_intent_id`. `withdraw()`
always returns `estimated_network_fee`/`estimated_recipient_amount`/`status` — never just
success/failure.
