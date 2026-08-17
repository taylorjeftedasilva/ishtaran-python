# Core API

Cobertura completa e literal da API real — 83 rotas, 16 módulos (ver `SDK_FEATURE_MATRIX.md`,
`SDK_METHOD_MAP.md`). Nenhum endpoint inventado, nenhuma rota admin-only/platform-only exposta.

## Control Plane (sempre Member JWT)

`client.organizations`, `client.applications`, `client.environments`, `client.api_keys`,
`client.members`, `client.asset_network_catalog`, `client.webhook_endpoints`, `client.webhook_deliveries`.

## Data Plane (API Key ou Member JWT)

`client.accounts`, `client.transactions`, `client.deposits`, `client.ledger`, `client.settlements`,
`client.refunds`, `client.withdrawals`, `client.workflows`/`event_types`/`events`, `client.sandbox`.

## Exemplo — fluxo completo sem Easy Mode

```python
from decimal import Decimal

account = client.accounts.create(organization_id, "customer-123")
client.accounts.authorize_application(account.account_id, application_id)

txn = client.transactions.create(organization_id, application_id, None, asset_network_id, Decimal("100"), [payer, recipient])
intent = client.deposits.create_payment_intent(organization_id, txn.transaction_id, asset_network_id, Decimal("100"))
full_intent = client.deposits.get_payment_intent(intent.payment_intent_id)
# full_intent.deposit_address -- endereço real para observar on-chain

settlement = client.settlements.execute_settlement(txn.transaction_id)
```

## Objetos anônimos reais

Vários POSTs reais devolvem um objeto mínimo (`CreateAccountResult(account_id=...)`,
`CreateTransactionResult(transaction_id=...)`) em vez do recurso completo — confirmado no
código-fonte dos handlers reais. Busque o recurso completo com o `get(...)` correspondente.

## Paginação real (generators lazy)

Só 2 endpoints têm paginação real: `withdrawals.list`/`.list_all` e
`ledger.list_entries`/`.list_all_entries`. Os `.list_all*` são generators — buscam a próxima página
sob demanda:

```python
for withdrawal in client.withdrawals.list_all(organization_id, page_size=20):
    print(withdrawal.withdrawal_id)
```
