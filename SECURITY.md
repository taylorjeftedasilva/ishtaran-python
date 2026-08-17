# Security

Ver `SECURITY_REVIEW.md` para o checklist formal completo.

## Segredos nunca vazam

`api_key`/`endpoint_secret`/tokens nunca aparecem em log, exceção, ou `repr()`.
`IshtaranClientConfig.__repr__` mascara a API Key. Logging opt-in nunca loga
`Authorization`/`X-Api-Key` em texto puro nem o corpo bruto.

## TLS

Verificado por padrão (comportamento nativo do `httpx`), sem switch de desabilitar exposto por
este SDK.

## Webhook

`hmac.compare_digest` (tempo constante real da stdlib), valida timestamp contra replay, nunca loga
o secret.

## Dependências

Mínimas: `httpx` (única dependência de produção — transporte HTTP síncrono maduro/amplamente
usado). `hashlib`/`hmac`/`json`/`decimal` nativos do stdlib, zero dependência de terceiros para
precisão de dinheiro (`json.loads(parse_float=Decimal, parse_int=Decimal)`) ou HMAC.
