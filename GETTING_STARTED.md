# Getting Started

## 1. Install

```bash
pip install -e ".[dev]"   # local, see README.md — not yet published on PyPI
```

## 2. Build the client

```python
import os
from ishtaran import IshtaranClient, Environment

client = IshtaranClient.create(
    api_key=os.environ["ISHTARAN_API_KEY"],
    environment=Environment.LOCAL,
)
```

`Environment.SANDBOX`/`PRODUCTION` don't have a known real URL yet — use an explicit `base_url=`
(see [`CONFIGURATION.md`](CONFIGURATION.md)).

## 3. Check a balance (Easy Mode)

```python
balance = client.get_balance(account_id, asset_network_id)
print("Available:", balance.available)  # decimal.Decimal
```

## 4. Receive a payment (Easy Mode)

```python
from decimal import Decimal

payment = client.receive_payment(organization_id, application_id, payer_account_id, recipient_account_id, asset_network_id, Decimal("100"))
print("Deposit address:", payment.deposit_address)

finished = client.wait_for_payment(payment.transaction_id, payment.payment_intent_id, timeout_seconds=600, poll_interval_seconds=5)
```

## 5. Withdrawal with visible Network Fee (Easy Mode)

```python
withdrawal = client.withdraw(organization_id, account_id, asset_network_id, Decimal("50"), "TDestinationAddressReal")
print(f"You receive {withdrawal.estimated_recipient_amount} (fee: {withdrawal.estimated_network_fee})")
```

## 6. Or use Core directly

```python
account = client.accounts.get(account_id)
quote = client.withdrawals.quote(organization_id, account_id, destination_id, asset_network_id, Decimal("50"))
```

## Next steps

- [`AUTHENTICATION.md`](AUTHENTICATION.md), [`EASY_MODE.md`](EASY_MODE.md), [`ERROR_HANDLING.md`](ERROR_HANDLING.md)
- [`examples/`](examples/) — 11 numbered examples
