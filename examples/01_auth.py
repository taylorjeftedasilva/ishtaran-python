"""01 -- Quickstart minimo: API key -> client -> primeira chamada util."""

import os

from ishtaran import Environment, IshtaranClient

client = IshtaranClient.create(api_key=os.environ.get("ISHTARAN_API_KEY"), environment=Environment.LOCAL)

print(f"Client Ishtaran pronto: {type(client.accounts).__name__} disponivel.")
