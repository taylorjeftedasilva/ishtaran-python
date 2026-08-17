# Getting Started

## 1. Instale

```bash
pip install -e ".[dev]"   # local, ver README.md — ainda não publicado no PyPI
```

## 2. Construa o client

```python
import os
from ishtaran import IshtaranClient, Environment

client = IshtaranClient.create(
    api_key=os.environ["ISHTARAN_API_KEY"],
    environment=Environment.LOCAL,
)
```

`Environment.SANDBOX`/`PRODUCTION` ainda não têm URL real conhecida — use `base_url=` explícito
(ver [`CONFIGURATION.md`](CONFIGURATION.md)).

## 3. Consulte um saldo (Easy Mode)

```python
balance = client.get_balance(account_id, asset_network_id)
print("Available:", balance.available)  # decimal.Decimal
```

## 4. Receba um pagamento (Easy Mode)

```python
from decimal import Decimal

payment = client.receive_payment(organization_id, application_id, payer_account_id, recipient_account_id, asset_network_id, Decimal("100"))
print("Deposit address:", payment.deposit_address)

finished = client.wait_for_payment(payment.transaction_id, payment.payment_intent_id, timeout_seconds=600, poll_interval_seconds=5)
```

## 5. Saque com Network Fee visível (Easy Mode)

```python
withdrawal = client.withdraw(organization_id, account_id, asset_network_id, Decimal("50"), "TDestinationAddressReal")
print(f"Você recebe {withdrawal.estimated_recipient_amount} (taxa: {withdrawal.estimated_network_fee})")
```

## 6. Ou use o Core diretamente

```python
account = client.accounts.get(account_id)
quote = client.withdrawals.quote(organization_id, account_id, destination_id, asset_network_id, Decimal("50"))
```

## Próximos passos

- [`AUTHENTICATION.md`](AUTHENTICATION.md), [`EASY_MODE.md`](EASY_MODE.md), [`ERROR_HANDLING.md`](ERROR_HANDLING.md)
- [`examples/`](examples/) — 11 exemplos numerados
