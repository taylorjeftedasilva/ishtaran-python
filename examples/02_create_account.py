"""02 -- Criar uma Account e consulta-la de volta (Core API)."""

import os

from ishtaran import Environment, IshtaranClient

client = IshtaranClient.create(api_key=os.environ.get("ISHTARAN_API_KEY"), environment=Environment.LOCAL)
organization_id = os.environ["ISHTARAN_ORGANIZATION_ID"]

created = client.accounts.create(organization_id, "customer-example-002")
print("Account criada:", created.account_id)

account = client.accounts.get(created.account_id)
print("Status:", account.status, "externalId=", account.external_id)
