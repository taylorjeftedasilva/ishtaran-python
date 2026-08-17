# Idempotency

Dois mecanismos reais (ver `SDK_CAPABILITY_SPEC.md` §9):

## Campo de corpo — todo endpoint financeiro

`transactions.create`, `deposits.create_payment_intent`, `settlements.execute_settlement`,
`refunds.execute_refund`, `withdrawals.request`, `events.ingest` — parâmetro opcional
`idempotency_key`; omitido, o SDK gera um UUID v4 automaticamente; explícito, nunca sobrescrito.

## Header `Idempotency-Key` — só 2 endpoints reais

`organizations.create(...)` e `organizations.create_application(...)` — os únicos 2 lugares do
backend que usam header em vez de campo de corpo (confirmado em código-fonte). Mesma política de
auto-geração.

## Reenvio

Mesma chave + mesmo payload = seguro (replay). Mesma chave + payload diferente =
`IdempotencyConflictError` (409). Retry automático (`RETRIES.md`) reusa a mesma chave da primeira
tentativa, nunca gera uma nova por tentativa.
