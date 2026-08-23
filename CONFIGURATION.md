# Configuration

```python
client = IshtaranClient.create(
    api_key="...",
    environment=Environment.LOCAL,
    base_url="http://localhost:8080",  # always explicit when present
    connect_timeout_seconds=5.0,       # default
    request_timeout_seconds=30.0,      # default
    enable_logging=True,               # opt-in, never on by default
)
```

## `base_url`/`Environment`

| Environment | Default | Explicit `base_url`? |
|---|---|---|
| `LOCAL` | `http://localhost:8080` | No |
| `SANDBOX`/`PRODUCTION` | **none** — infra not yet provisioned | **Yes, required** |

Constructing without `base_url` for `SANDBOX`/`PRODUCTION` raises `ValueError` immediately — it
never points to a made-up URL.

## TLS

Verified by default (native `httpx` behavior); never disabled by this SDK.

## Redirects

`httpx.Client(follow_redirects=False)` — any 3xx is treated as a `NetworkError`, never followed
automatically (same policy as Java/TypeScript).

## User-Agent

`ishtaran-python/<version>` — fixed, no personal data.
