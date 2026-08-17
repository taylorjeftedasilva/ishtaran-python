# Easy Mode vs. Core API

## Use Easy Mode quando...

- Quer integrar rápido: `client.receive_payment(...)`, `client.withdraw(...)`, `client.get_balance(...)`.
- Precisa esperar um resultado assíncrono com segurança: `client.wait_for_payment(...)`,
  `client.withdrawals.wait_for(...)`, `client.transactions.wait_for(...)` — sempre com timeout.
- Só precisa verificar uma assinatura de webhook: `client.verify_webhook_signature(...)`.

## Use Core API quando...

- Precisa de controle granular (`client.transactions.reserve(...)` vs. `client.settlements.execute_settlement(...)`).
- Precisa de um recurso que o Easy Mode não cobre — 93 operações reais, ver `SDK_FEATURE_MATRIX.md`.
- Quer paginar de verdade: `client.withdrawals.list_all(...)`/`client.ledger.list_all_entries(...)`
  (generators lazy) em vez de uma única chamada.

## Equivalência concreta

| Easy Mode | Core equivalente |
|---|---|
| `client.receive_payment(...)` | `transactions.create()` + `deposits.create_payment_intent()` + `deposits.get_payment_intent()` |
| `client.withdraw(...)` | `withdrawals.create_destination()` + `withdrawals.request()` |
| `client.get_balance(...)` | `ledger.get_balance(...)` |

Easy Mode nunca esconde `withdrawal_id`/`transaction_id`/`payment_intent_id` reais. `withdraw()`
sempre devolve `estimated_network_fee`/`estimated_recipient_amount`/`status` — nunca só sucesso/falha.
