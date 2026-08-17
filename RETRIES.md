# Retries

| Cenário | Retry? |
|---|---|
| Falha de conexão | Sempre |
| HTTP 429 | Sempre — respeita `Retry-After` real |
| HTTP 5xx | Só se idempotente (GET, ou POST/DELETE com Idempotency-Key) |
| 400/401/403/404/409/422 | **Nunca** — determinísticos |

Defaults: até 2 tentativas adicionais, backoff exponencial com jitter (base 200ms, fator 2x, teto
5s). Ver `ishtaran.RetryPolicy`.

Um 5xx genuíno pode ter processado parcialmente o efeito — reintentar POST sem Idempotency-Key
correria o risco de duplicar. O SDK nunca faz isso.
