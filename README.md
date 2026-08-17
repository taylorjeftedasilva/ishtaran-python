# Ishtaran Python SDK

SDK oficial em Python para a [API Ishtaran](https://ishtaran.com) — plataforma financeira
programável. Terceira implementação do [Ishtaran Official SDK Program](../../SDK_CAPABILITY_SPEC.md)
(Java → TypeScript → **Python** → Go), 100% de paridade funcional com o Java (SDK de referência).

## Duas camadas, mesmo backend

- **Easy Mode** — `client.receive_payment(...)`, `client.withdraw(...)`, `client.get_balance(...)`,
  `client.verify_webhook_signature(...)`: composição rápida, nunca duplica lógica de negócio.
- **Core API** — `client.accounts`, `client.transactions`, `client.withdrawals`, etc.: acesso
  granular aos mesmos 83 endpoints reais da API (ver [`SDK_FEATURE_MATRIX.md`](../../SDK_FEATURE_MATRIX.md)).

## Instalação

Ainda não publicado no PyPI (decisão de licenciamento pendente). Para uso local:

```bash
cd sdks/python
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

Requer **Python 3.10+**.

## Quickstart

```python
from ishtaran import IshtaranClient, Environment

client = IshtaranClient.create(
    api_key=os.environ["ISHTARAN_API_KEY"],
    environment=Environment.LOCAL,  # ou SANDBOX/PRODUCTION com base_url explícito
)

balance = client.get_balance(account_id, asset_network_id)
print("Available:", balance.available)  # decimal.Decimal, nunca float
```

Veja [`GETTING_STARTED.md`](GETTING_STARTED.md) e [`examples/`](examples/).

## Dinheiro é sempre `Decimal`

Todo campo monetário é tipado como `decimal.Decimal` — nunca `float`. A API real envia dinheiro
como `number(double)` no JSON; o parser padrão do Python (`float`) já perderia precisão antes do
SDK poder intervir, então todo parsing de resposta usa `json.loads(text, parse_float=Decimal,
parse_int=Decimal)`, preservando o texto exato de todo número. Ver
[`SDK_CAPABILITY_SPEC.md` §11.1](../../SDK_CAPABILITY_SPEC.md#111-dinheiro).

## Documentação

| Documento | Conteúdo |
|---|---|
| [GETTING_STARTED.md](GETTING_STARTED.md) | Primeiro uso |
| [AUTHENTICATION.md](AUTHENTICATION.md) | `X-Api-Key` vs. Member JWT |
| [EASY_MODE.md](EASY_MODE.md) | Quando usar Easy Mode vs. Core |
| [CORE_API.md](CORE_API.md) | Cobertura completa de recursos |
| [ERROR_HANDLING.md](ERROR_HANDLING.md) | Hierarquia `IshtaranError` |
| [IDEMPOTENCY.md](IDEMPOTENCY.md) | Chave automática vs. explícita |
| [RETRIES.md](RETRIES.md) | Política de retry |
| [WEBHOOKS.md](WEBHOOKS.md) | Verificação de assinatura |
| [CONFIGURATION.md](CONFIGURATION.md) | Configuração do client |
| [SECURITY.md](SECURITY.md) | Segredos, TLS, redação |
| [FEATURES.md](FEATURES.md) | Cobertura de capacidades |
| [CHANGELOG.md](CHANGELOG.md) | Histórico de versões |

Todo comportamento é extraído da API real, nunca inventado — ver [`SDK_CAPABILITY_SPEC.md`](../../SDK_CAPABILITY_SPEC.md).

## Nota sobre sync/async

Esta versão é **síncrona** (`httpx.Client`) — mesma pacing permitida ao Java ("sync-first
inicialmente") pelo brief do SDK Program. Suporte assíncrono (`httpx.AsyncClient`, `async`/`await`
com paridade real de API) fica como extensão futura documentada, não uma limitação escondida.
