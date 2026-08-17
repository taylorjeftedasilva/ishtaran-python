# SECURITY_REVIEW.md — Ishtaran Python SDK

Checklist do §57 do brief do SDK Program. Mesma disciplina do Java/TypeScript: cada item com
evidência real (teste ou leitura de código), nunca assumido.

| # | Item | Status | Evidência |
|---|---|---|---|
| 1 | Secrets nunca logados | ✅ PASS | `test_logging_transport.py` — `redacted_headers` nunca expõe API Key/Authorization em texto puro |
| 2 | API Key nunca na URL/querystring | ✅ PASS | `AuthenticatingTransport` só anexa via header; nenhum resource constrói URL com a chave |
| 3 | TLS verificado por padrão | ✅ PASS | `httpx.Client` verifica certificado por padrão; nenhum switch de desabilitar exposto por este SDK |
| 4 | Comparação de assinatura de webhook em tempo constante | ✅ PASS | `hmac.compare_digest` real (stdlib) — `test_webhook_signature_verifier.py` (7 testes, incluindo vetor calculado independentemente via `hmac`/`hashlib` direto, mesmo vetor usado nas 3 linguagens) |
| 5 | Retries seguros (nunca cegos em mutação não-idempotente) | ✅ PASS | `test_retrying_transport.py` — nunca retry em 400/401/403/404/409/422; 5xx só com idempotência/GET |
| 6 | Timeout obrigatório, nunca infinito | ✅ PASS | `httpx.Timeout(connect=..., read=..., write=..., pool=...)` sempre aplicado; defaults finitos (`test_client_config.py`) |
| 7 | Redação central em logging opt-in | ✅ PASS | `LoggingTransport` nunca loga corpo bruto, só método/path/status/duração |
| 8 | Dependências mínimas, escaneadas | ✅ PASS | 1 dependência de produção (`httpx`, madura/amplamente usada, mantida ativamente). Nenhuma dependência de terceiros para precisão de dinheiro (stdlib `decimal`/`json`) ou HMAC (stdlib `hmac`/`hashlib`) |
| 9 | Dinheiro nunca perde precisão | ✅ PASS | `test_json_util.py` — `json.loads(parse_float=Decimal, parse_int=Decimal)` preserva o texto exato; teste explícito confirmando que `float()` nativo TERIA perdido essa precisão |
| 10 | Resposta maliciosa/malformada nunca derruba o client | ✅ PASS | `test_error_mapper.py` — corpo malformado nunca levanta exceção de parsing; enums desconhecidos nunca levantam (`test_enums.py`) |
| 11 | Corpo de resposta com tamanho ilimitado | ⚠️ **LIMITAÇÃO REAL, NÃO CORRIGIDA** | `httpx.Client.request()` buferiza a resposta inteira em memória sem limite configurável nesta versão. Mesma limitação documentada nos SDKs Java/TypeScript |
| 12 | Desserialização segura | ✅ PASS | `json.loads` nunca faz desserialização polimórfica/reflection-based — sempre produz dados estruturais simples, mapeados manualmente para `dataclasses` conhecidos |
| 13 | URL controlada pelo usuário / SSRF | ✅ PASS | `base_url` sempre explícito e fixado na construção do client — nenhum método de negócio aceita override de URL (verificado: nenhum método em `resources/*.py` recebe parâmetro de URL) |
| 14 | Comportamento de redirecionamento HTTP | ✅ PASS | `httpx.Client(follow_redirects=False)` desde a primeira versão deste SDK — qualquer 3xx é tratado como `NetworkError`, nunca seguido automaticamente. Aplicado **proativamente** nesta linguagem, aprendendo do achado real corrigido no SDK TypeScript (nunca reintroduzido aqui) |
| 15 | Injeção de header | ✅ PASS | `httpx`/`h11` validam nomes/valores de header (rejeitam CR/LF) — nunca construído por concatenação de string crua |
| 16 | Injeção de query string | ✅ PASS (achado real corrigido nesta revisão) | Ver "Achado corrigido" abaixo |
| 17 | Comportamento de proxy | N/A | Não aplicável — nenhuma configuração de proxy customizada exposta; `httpx` usa o comportamento padrão do ambiente |

## Achado corrigido durante esta revisão

**`date_from`/`date_to` concatenados crus na query string** de `WithdrawalsResource.list` e
`LedgerResource.list_entries` — mesma classe de risco já encontrada e corrigida no SDK Java
(`eventType` em `WebhookEndpointsResource`) e prevenida desde o início no SDK TypeScript (via
`URLSearchParams`). Um valor malicioso em `date_from` (ex. `"2026-01-01&take=99999"`) poderia
injetar um parâmetro de query não intencional. Corrigido com `urllib.parse.urlencode` em ambos os
métodos — `WebhookEndpointsResource.list_deliveries` já usava esse padrão desde a implementação
inicial (nunca teve o bug). Coberto por `test_query_encoding_safety.py`.

## Verificação estática adicional (além do checklist do brief)

`mypy --strict` limpo em todos os 63 módulos do SDK (`python -m mypy src/ishtaran` →
`Success: no issues found`) — reduz a superfície de bugs de tipo que poderiam se manifestar como
comportamento inseguro em tempo de execução (ex.: `None` não tratado, tipo incorreto passado para
serialização).

## Limitações conhecidas (documentadas, não escondidas)

1. **Corpo de resposta sem limite de tamanho** (item 11) — mesma limitação dos SDKs Java/
   TypeScript, mesma justificativa (risco só existe se `base_url` apontar para um host
   comprometido).
2. **`EnumRegistry` usa `setattr` dinâmico** — `WithdrawalStatus.COMPLETED` etc. não são
   estaticamente conhecidos pelo mypy sem `# type: ignore[attr-defined]` no ponto de uso; não é um
   risco de segurança (o valor em runtime é sempre correto, só a checagem estática não cobre esse
   caso específico), mas é uma limitação de tipagem documentada.
3. **Síncrono apenas** — não é um item de segurança, mas afeta o modelo de concorrência do
   consumidor (ver `CHANGELOG.md`).

## Veredito

**PASS**, com 3 limitações documentadas explicitamente — nenhum achado crítico ou de alta
severidade permanece sem correção ou sem justificativa registrada; o único achado real de
comportamento (injeção de query string) foi corrigido, não apenas anotado.
