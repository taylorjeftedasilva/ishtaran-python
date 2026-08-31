"""07 -- Quote a withdrawal BEFORE committing the amount (pure read, never reserves balance)."""

import os
from decimal import Decimal

from ishtaran import Environment, IshtaranClient

client = IshtaranClient.create(api_key=os.environ.get("ISHTARAN_API_KEY"), environment=Environment.LOCAL)

organization_id = os.environ["ISHTARAN_ORGANIZATION_ID"]
environment_id = os.environ["ISHTARAN_ENVIRONMENT_ID"]
account_id = os.environ["ISHTARAN_PAYER_ACCOUNT_ID"]
destination_id = os.environ["ISHTARAN_WITHDRAWAL_DESTINATION_ID"]
asset_network_id = os.environ["ISHTARAN_ASSET_NETWORK_ID"]

quote = client.withdrawals.quote(organization_id, environment_id, account_id, destination_id, asset_network_id, Decimal("50"))
print("requested_amount=", quote.requested_amount)
# Under SelfCustody the beneficiary always receives the full requested_amount -- estimated_network_fee
# is deprecated and always None. network_execution_cost is the real network cost (paid separately,
# per the registered NetworkCostPayerAccount, never subtracted from what the beneficiary receives).
print("estimated_recipient_amount=", quote.estimated_recipient_amount)
print("network_execution_cost=", quote.network_execution_cost)
print("expires_at=", quote.expires_at)
