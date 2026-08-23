from __future__ import annotations

from .resource_support import ResourceSupport
from ..http.types import HttpTransport, delete_request, get_request, post_request
from ..model.account_holders import (
    CreateAccountHolderInvitationResult,
    OrganizationAccountResponse,
    map_create_account_holder_invitation_result,
    map_organization_account_response,
)
from ..model.data_plane import AccountResponse, CreateAccountResult, map_account_response, map_create_account_result


class AccountsResource(ResourceSupport):
    """Data Plane -- Accounts (9 real routes, DEC-032)."""

    def __init__(self, transport: HttpTransport) -> None:
        super().__init__(transport)

    def create(self, organization_id: str, external_id: str) -> CreateAccountResult:
        body = self._to_json({"externalId": external_id})
        return self._execute(post_request(f"/v1/organizations/{organization_id}/accounts", body, False), map_create_account_result)

    def list(self, organization_id: str) -> list[OrganizationAccountResponse]:
        """Returns this Organization's link (Relationship) with each Account -- never the Account in isolation (DEC-032)."""
        return self._execute_list(get_request(f"/v1/organizations/{organization_id}/accounts"), map_organization_account_response)

    def get(self, account_id: str) -> AccountResponse:
        return self._execute(get_request(f"/v1/accounts/{account_id}"), map_account_response)

    def authorize_application(self, organization_id: str, account_id: str, application_id: str) -> None:
        """DEC-032 -- route nested under organization_id (formerly /v1/accounts/{accountId}/authorize-application):
        the backend revalidates the Relationship (organizationId, Account.AccountHolderId) internally."""
        body = self._to_json({"applicationId": application_id})
        self._execute_no_content(
            post_request(f"/v1/organizations/{organization_id}/accounts/{account_id}/authorize-application", body, False)
        )

    def freeze(self, account_id: str, reason: str | None = None) -> None:
        body = self._to_json({"reason": reason or ""})
        self._execute_no_content(post_request(f"/v1/accounts/{account_id}/freeze", body, False))

    def unfreeze(self, account_id: str) -> None:
        self._execute_no_content(post_request(f"/v1/accounts/{account_id}/unfreeze", None, False))

    def close(self, account_id: str) -> None:
        self._execute_no_content(delete_request(f"/v1/accounts/{account_id}"))

    def create_account_holder_invitation(self, organization_id: str, external_id: str | None = None) -> CreateAccountHolderInvitationResult:
        """DEC-032/BR-HLD-005 -- issues an invitation for an AccountHolder to relate to this Organization.
        plain_text_token exists only in this response, exactly once -- treat it as a secret."""
        body = self._to_json({"externalId": external_id})
        return self._execute(
            post_request(f"/v1/organizations/{organization_id}/account-holder-invitations", body, False),
            map_create_account_holder_invitation_result,
        )

    def revoke_relationship(self, organization_id: str, relationship_id: str) -> None:
        """DEC-032/BR-ACC-008 -- never deletes the AccountHolder/Account, only removes this Organization's authorization."""
        self._execute_no_content(post_request(f"/v1/organizations/{organization_id}/relationships/{relationship_id}/revoke", None, False))
