"""
03 -- Receber um pagamento via Easy Mode: compoe Transaction + Payment Intent, devolve o
deposit_address real com os IDs reais do Core para debugging.
"""

import os
from decimal import Decimal

from ishtaran import Environment, IshtaranClient

client = IshtaranClient.create(api_key=os.environ.get("ISHTARAN_API_KEY"), environment=Environment.LOCAL)

organization_id = os.environ["ISHTARAN_ORGANIZATION_ID"]
application_id = os.environ["ISHTARAN_APPLICATION_ID"]
payer_account_id = os.environ["ISHTARAN_PAYER_ACCOUNT_ID"]
recipient_account_id = os.environ["ISHTARAN_RECIPIENT_ACCOUNT_ID"]
asset_network_id = os.environ["ISHTARAN_ASSET_NETWORK_ID"]

payment = client.receive_payment(organization_id, application_id, payer_account_id, recipient_account_id, asset_network_id, Decimal("100"))
print("transaction_id=", payment.transaction_id)
print("payment_intent_id=", payment.payment_intent_id)
print("deposit_address=", payment.deposit_address)

finished = client.wait_for_payment(payment.transaction_id, payment.payment_intent_id, timeout_seconds=600, poll_interval_seconds=5)
print("Status final:", finished.payment_intent_status.name)
