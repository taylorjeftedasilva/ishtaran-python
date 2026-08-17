# Features

Derivado de [`SDK_FEATURE_MATRIX.md`](../../SDK_FEATURE_MATRIX.md). Core API: 93/93 operações
reais (16/16 módulos). Easy Mode: 100%. Cross-cutting: 100% (config, auth, erros, retry,
idempotência, paginação, enums forward-compatible, segurança/redação, logging opt-in, wait_for
seguro, empacotamento validado wheel+sdist).

100% de paridade funcional com o Java (SDK de referência) — mesmos nomes de conceito de negócio,
mesmos defaults, mesma política de retry/idempotência/timeout, diferindo só no idioma da linguagem
(`client.withdrawals.quote(...)` idêntico em Python e TypeScript; Java usa `client.withdrawals().quote(...)`).

## Extra em relação ao Java/TypeScript

- `mypy --strict` limpo (verificação estática completa).
- Dinheiro como `decimal.Decimal` nativo — mais idiomático que o `string` do TypeScript, sem
  dependência de terceiros para precisão (o stdlib `json`/`decimal` já resolvem o problema).
