"""07 -- Quote a withdrawal BEFORE committing the amount (pure read, never reserves balance)."""

import os
from decimal import Decimal

from ishtaran import Environment, IshtaranClient

client = IshtaranClient.create(api_key=os.environ.get("ISHTARAN_API_KEY"), environment=Environment.LOCAL)

organization_id = os.environ["ISHTARAN_ORGANIZATION_ID"]
account_id = os.environ["ISHTARAN_PAYER_ACCOUNT_ID"]
destination_id = os.environ["ISHTARAN_WITHDRAWAL_DESTINATION_ID"]
asset_network_id = os.environ["ISHTARAN_ASSET_NETWORK_ID"]

quote = client.withdrawals.quote(organization_id, account_id, destination_id, asset_network_id, Decimal("50"))
print("requested_amount=", quote.requested_amount)
print("estimated_network_fee=", quote.estimated_network_fee)
print("estimated_recipient_amount=", quote.estimated_recipient_amount)
print("expires_at=", quote.expires_at)
