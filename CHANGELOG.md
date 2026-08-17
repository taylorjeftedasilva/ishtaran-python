# Changelog

Segue [SemVer](https://semver.org/). Ainda não publicado (PyPI).

## [1.0.0.dev0] — 2026-08-17

Terceira implementação do Ishtaran Official SDK Program — 100% de paridade funcional com o Java
(SDK de referência).

### Adicionado

- Client central (`IshtaranClient.create(...)`).
- Core API completo — 16 módulos, 93 operações reais.
- Easy Mode — `receive_payment`/`get_payment`/`wait_for_payment`, `withdraw`, `get_balance`,
  `verify_webhook_signature`.
- Autenticação `X-Api-Key` + Member JWT.
- Hierarquia `IshtaranError` completa.
- Retry seguro com backoff+jitter.
- Idempotência (body e header, conforme o endpoint real).
- Paginação real via generators lazy.
- Enums forward-compatible (`from_raw`/`is_unknown`, fallback `UNKNOWN`).
- Dinheiro sempre `decimal.Decimal` (nunca `float`), via `json.loads(parse_float=Decimal,
  parse_int=Decimal)`.
- `verify_webhook_signature`/`compute_webhook_signature` (HMAC-SHA256, tempo constante).
- Logging opt-in com redação central.
- Redirects HTTP nunca seguidos automaticamente (`follow_redirects=False`).
- `mypy --strict` limpo em todos os 63 módulos do SDK.
- Empacotamento validado — wheel + sdist reais (`python -m build`), instalados em venv limpo.

### Conhecido, ainda pendente

- Síncrono apenas nesta versão (`httpx.Client`) — suporte assíncrono é extensão futura documentada,
  mesma pacing permitida ao Java ("sync-first inicialmente").
- Publicação real no PyPI — bloqueada por decisão de licenciamento pendente.
