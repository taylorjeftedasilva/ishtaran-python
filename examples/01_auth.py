"""01 -- Minimal quickstart: API key -> client -> first useful call."""

import os

from ishtaran import Environment, IshtaranClient

client = IshtaranClient.create(api_key=os.environ.get("ISHTARAN_API_KEY"), environment=Environment.LOCAL)

print(f"Ishtaran client ready: {type(client.accounts).__name__} available.")
