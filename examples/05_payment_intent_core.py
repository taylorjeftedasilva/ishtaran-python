"""
05 -- Create a Payment Intent via the Core API. The real deposit_address only appears on the
dedicated GET (never in the creation POST's response -- real API behavior, not an SDK limitation).
"""

import os
from decimal import Decimal

from ishtaran import Environment, IshtaranClient

client = IshtaranClient.create(api_key=os.environ.get("ISHTARAN_API_KEY"), environment=Environment.LOCAL)

organization_id = os.environ["ISHTARAN_ORGANIZATION_ID"]
transaction_id = os.environ["ISHTARAN_TRANSACTION_ID"]
asset_network_id = os.environ["ISHTARAN_ASSET_NETWORK_ID"]

created = client.deposits.create_payment_intent(organization_id, transaction_id, asset_network_id, Decimal("250"))
full = client.deposits.get_payment_intent(created.payment_intent_id)
print("deposit_address=", full.deposit_address)
print("status=", full.status.name)
