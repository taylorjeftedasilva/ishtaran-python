# Configuration

```python
client = IshtaranClient.create(
    api_key="...",
    environment=Environment.LOCAL,
    base_url="http://localhost:8080",  # sempre explícito quando presente
    connect_timeout_seconds=5.0,       # default
    request_timeout_seconds=30.0,      # default
    enable_logging=True,               # opt-in, nunca ligado por padrão
)
```

## `base_url`/`Environment`

| Environment | Default | `base_url` explícito? |
|---|---|---|
| `LOCAL` | `http://localhost:8080` | Não |
| `SANDBOX`/`PRODUCTION` | **nenhum** — infra ainda não provisionada | **Sim, obrigatório** |

Construir sem `base_url` para `SANDBOX`/`PRODUCTION` lança `ValueError` imediatamente — nunca
aponta para uma URL inventada.

## TLS

Verificado por padrão (comportamento nativo do `httpx`); nunca desabilitado por este SDK.

## Redirects

`httpx.Client(follow_redirects=False)` — qualquer 3xx é tratado como `NetworkError`, nunca seguido
automaticamente (mesma política do Java/TypeScript).

## User-Agent

`ishtaran-python/<versão>` — fixo, sem dado pessoal.
