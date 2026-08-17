# Error Handling

Toda exceção é subclasse de `IshtaranError` (ver `SDK_CAPABILITY_SPEC.md` §6):

```
IshtaranError
├── AuthenticationError       (401 — sem code/details)
├── AuthorizationError        (403 — idem)
├── ValidationError           (400, code=VALIDATION_ERROR — 1 string, nunca lista por campo)
├── NotFoundError             (404, code=NOT_FOUND)
├── ConflictError             (409 — vários code)
├── IdempotencyConflictError  (409, code=IDEMPOTENCY_KEY_CONFLICT — extends ConflictError)
├── RateLimitError            (429, code=RATE_LIMITED — retry_after_seconds)
├── NetworkError              (falha de transporte)
├── TimeoutError              (timeout de request, ou wait_for excedendo o prazo)
└── ApiError                  (fallback — preserva http_status/code/details brutos)
```

## Uso

```python
from ishtaran import ValidationError, RateLimitError, IshtaranError
import time

try:
    client.withdrawals.request(org_id, account_id, dest_id, asset_network_id, amount)
except ValidationError as e:
    print("Validação falhou:", e.message)
except RateLimitError as e:
    time.sleep(e.retry_after_seconds or 1)
except IshtaranError as e:
    print(f"Falha ({e.http_status}):", e.message)
```

## Campos disponíveis

`http_status`, `code`, `request_id` (sempre `None` hoje — API real não tem mecanismo de correlation
ID, §12.1), `details` (corpo bruto), `retryable`.

## Por que 401/403 não têm `code`/`details`

Nenhum `AuthenticationHandler` do backend registra challenge customizado — o middleware de
autenticação responde com corpo vazio antes de chegar no handler que produz `ProblemDetails`.

## Nota de nomenclatura

`ishtaran.TimeoutError` sombreia deliberadamente `builtins.TimeoutError`, para manter paridade
exata de nome com Java/TypeScript (regra do brief). Código interno do SDK que precisa do timeout de
rede real usa `httpx.TimeoutException`, não o builtin — sem colisão prática. Se seu código também
usa `builtins.TimeoutError`, importe com um alias: `from ishtaran import TimeoutError as
IshtaranTimeoutError`.
