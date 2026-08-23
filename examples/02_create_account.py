"""02 -- Create an Account and fetch it back (Core API)."""

import os

from ishtaran import Environment, IshtaranClient

client = IshtaranClient.create(api_key=os.environ.get("ISHTARAN_API_KEY"), environment=Environment.LOCAL)
organization_id = os.environ["ISHTARAN_ORGANIZATION_ID"]

created = client.accounts.create(organization_id, "customer-example-002")
print("Account created:", created.account_id)

account = client.accounts.get(created.account_id)
print("Status:", account.status, "accountHolderId=", account.account_holder_id)

# DEC-032 -- an Account no longer carries external_id/organization_id directly (global identity,
# linked to N Organizations via Relationship). To see this Organization's link to the Account
# (including external_id/authorized Applications), query the Organization-scoped list:
relationships = client.accounts.list(organization_id)
own = next(r for r in relationships if r.account_id == created.account_id)
print("Relationship:", own.relationship_id, "externalId=", own.external_id, "status=", own.relationship_status)
