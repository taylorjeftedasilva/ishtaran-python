# Error Handling

Every exception is a subclass of `IshtaranError` (see `SDK_CAPABILITY_SPEC.md` §6):

```
IshtaranError
├── AuthenticationError       (401 — no code/details)
├── AuthorizationError        (403 — same)
├── ValidationError           (400, code=VALIDATION_ERROR — 1 string, never a per-field list)
├── NotFoundError             (404, code=NOT_FOUND)
├── ConflictError             (409 — various codes)
├── IdempotencyConflictError  (409, code=IDEMPOTENCY_KEY_CONFLICT — extends ConflictError)
├── RateLimitError            (429, code=RATE_LIMITED — retry_after_seconds)
├── NetworkError              (transport failure)
├── TimeoutError              (request timeout, or wait_for exceeding its deadline)
└── ApiError                  (fallback — preserves raw http_status/code/details)
```

## Usage

```python
from ishtaran import ValidationError, RateLimitError, IshtaranError
import time

try:
    client.withdrawals.request(org_id, account_id, dest_id, asset_network_id, amount)
except ValidationError as e:
    print("Validation failed:", e.message)
except RateLimitError as e:
    time.sleep(e.retry_after_seconds or 1)
except IshtaranError as e:
    print(f"Failed ({e.http_status}):", e.message)
```

## Available fields

`http_status`, `code`, `request_id` (always `None` today — the real API has no correlation ID
mechanism, §12.1), `details` (raw body), `retryable`.

## Why 401/403 have no `code`/`details`

No backend `AuthenticationHandler` registers a custom challenge — the authentication middleware
responds with an empty body before reaching the handler that produces `ProblemDetails`.

## Naming note

`ishtaran.TimeoutError` deliberately shadows `builtins.TimeoutError`, to keep exact name parity
with Java/TypeScript (rule from the brief). Internal SDK code that needs the real network timeout
uses `httpx.TimeoutException`, not the builtin — no practical collision. If your own code also
uses `builtins.TimeoutError`, import with an alias: `from ishtaran import TimeoutError as
IshtaranTimeoutError`.
