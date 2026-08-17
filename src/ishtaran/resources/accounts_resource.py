from __future__ import annotations

from .resource_support import ResourceSupport
from ..http.types import HttpTransport, delete_request, get_request, post_request
from ..model.data_plane import AccountResponse, CreateAccountResult, map_account_response, map_create_account_result


class AccountsResource(ResourceSupport):
    """Data Plane -- Accounts (7 rotas reais)."""

    def __init__(self, transport: HttpTransport) -> None:
        super().__init__(transport)

    def create(self, organization_id: str, external_id: str) -> CreateAccountResult:
        body = self._to_json({"externalId": external_id})
        return self._execute(post_request(f"/v1/organizations/{organization_id}/accounts", body, False), map_create_account_result)

    def list(self, organization_id: str) -> list[AccountResponse]:
        return self._execute_list(get_request(f"/v1/organizations/{organization_id}/accounts"), map_account_response)

    def get(self, account_id: str) -> AccountResponse:
        return self._execute(get_request(f"/v1/accounts/{account_id}"), map_account_response)

    def authorize_application(self, account_id: str, application_id: str) -> None:
        body = self._to_json({"applicationId": application_id})
        self._execute_no_content(post_request(f"/v1/accounts/{account_id}/authorize-application", body, False))

    def freeze(self, account_id: str, reason: str | None = None) -> None:
        body = self._to_json({"reason": reason or ""})
        self._execute_no_content(post_request(f"/v1/accounts/{account_id}/freeze", body, False))

    def unfreeze(self, account_id: str) -> None:
        self._execute_no_content(post_request(f"/v1/accounts/{account_id}/unfreeze", None, False))

    def close(self, account_id: str) -> None:
        self._execute_no_content(delete_request(f"/v1/accounts/{account_id}"))
