"""12 -- Invite an AccountHolder to link with an Organization, and claim the invitation from the
holder's side (DEC-032). Two "personas" in the same process purely for illustration -- in real
life, the plain_text_token goes out over a separate channel (email/link) and it's the holder
themself who calls sign_up_and_claim_invitation, never the Organization on their behalf."""

import os

from ishtaran import Environment, IshtaranClient

client = IshtaranClient.create(api_key=os.environ.get("ISHTARAN_API_KEY"), environment=Environment.LOCAL)
organization_id = os.environ["ISHTARAN_ORGANIZATION_ID"]

# Organization side: issues the invitation. plain_text_token only exists in this response --
# treat it as a secret, deliver it to the holder outside the API (never log/persist it in plain text).
invitation = client.accounts.create_account_holder_invitation(organization_id, "customer-example-012")
print("Invitation issued:", invitation.invitation_id, "expires at", invitation.expires_at)

# Holder (AccountHolder) side: never seen before, creates the identity and claims the
# invitation atomically. No prior authentication -- the invitation token itself is proof of possession.
claim = client.account_holders.sign_up_and_claim_invitation(
    invitation.plain_text_token, "holder-example-012@example.com", "Str0ngP@ssw0rd!"
)

if not claim.success:
    raise RuntimeError(f"Failed to claim invitation: {claim.error_code}")
print("Relationship created:", claim.relationship_id)

# The AccessToken returned (via sign_up_and_claim_invitation) already populated this client's
# AccountHolder session -- me() works immediately, no need to call login() again.
me = client.account_holders.me()
print("AccountHolder:", me.account_holder_id, "account=", me.account_id, "email=", me.email)
