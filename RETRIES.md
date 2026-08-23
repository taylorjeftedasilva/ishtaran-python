# Retries

| Scenario | Retry? |
|---|---|
| Connection failure | Always |
| HTTP 429 | Always — honors the real `Retry-After` |
| HTTP 5xx | Only if idempotent (GET, or POST/DELETE with Idempotency-Key) |
| 400/401/403/404/409/422 | **Never** — deterministic |

Defaults: up to 2 additional attempts, exponential backoff with jitter (200ms base, 2x factor,
5s cap). See `ishtaran.RetryPolicy`.

A genuine 5xx may have partially applied its effect — retrying a POST without an
Idempotency-Key would risk duplicating it. The SDK never does this.
