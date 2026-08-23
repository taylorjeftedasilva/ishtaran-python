# Idempotency

Two real mechanisms (see `SDK_CAPABILITY_SPEC.md` §9):

## Body field — every financial endpoint

`transactions.create`, `deposits.create_payment_intent`, `settlements.execute_settlement`,
`refunds.execute_refund`, `withdrawals.request`, `events.ingest` — optional parameter
`idempotency_key`; if omitted, the SDK generates a UUID v4 automatically; if explicit, it is
never overwritten.

## `Idempotency-Key` header — only 2 real endpoints

`organizations.create(...)` and `organizations.create_application(...)` — the only 2 places in
the backend that use a header instead of a body field (confirmed in source code). Same
auto-generation policy.

## Resubmission

Same key + same payload = safe (replay). Same key + different payload =
`IdempotencyConflictError` (409). Automatic retry (`RETRIES.md`) reuses the same key from the
first attempt, never generates a new one per attempt.
