"""04 -- Create a Transaction via the Core API, with granular control over participants."""

import os
from decimal import Decimal

from ishtaran import Environment, IshtaranClient
from ishtaran.model.data_plane import ParticipantInput

client = IshtaranClient.create(api_key=os.environ.get("ISHTARAN_API_KEY"), environment=Environment.LOCAL)

organization_id = os.environ["ISHTARAN_ORGANIZATION_ID"]
application_id = os.environ["ISHTARAN_APPLICATION_ID"]
payer_account_id = os.environ["ISHTARAN_PAYER_ACCOUNT_ID"]
recipient_account_id = os.environ["ISHTARAN_RECIPIENT_ACCOUNT_ID"]
asset_network_id = os.environ["ISHTARAN_ASSET_NETWORK_ID"]

participants = [
    ParticipantInput(account_id=payer_account_id, role="payer", is_payer=True),
    ParticipantInput(account_id=recipient_account_id, role="recipient", is_payer=False),
]

created = client.transactions.create(organization_id, application_id, None, asset_network_id, Decimal("250"), participants)
print("transaction_id=", created.transaction_id)

state = client.transactions.get_state(created.transaction_id)
print("Status:", state.status.name)
