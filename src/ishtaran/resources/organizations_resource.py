from __future__ import annotations

from .resource_support import ResourceSupport
from ..http.types import HttpTransport, get_request, post_request
from ..idempotency.idempotency_key_generator import resolve_idempotency_key
from ..model.control_plane import (
    ApplicationResponse,
    CreatedResourceResponse,
    OrganizationResponse,
    map_application_response,
    map_created_resource_response,
    map_organization_response,
)


class OrganizationsResource(ResourceSupport):
    """
    Control Plane -- Organizations (6 real routes). Always Member JWT. create/create_application
    use idempotency via the Idempotency-Key HEADER -- unlike the body-field pattern of the
    financial modules (see SDK_CAPABILITY_SPEC.md section 9).
    """

    def __init__(self, transport: HttpTransport) -> None:
        super().__init__(transport)

    def create(self, name: str, idempotency_key: str | None = None) -> CreatedResourceResponse:
        request = post_request("/v1/organizations", self._to_json({"name": name}), False)
        request = request.with_header("Idempotency-Key", resolve_idempotency_key(idempotency_key))
        return self._execute(request, map_created_resource_response)

    def get(self, organization_id: str) -> OrganizationResponse:
        return self._execute(get_request(f"/v1/organizations/{organization_id}"), map_organization_response)

    def suspend(self, organization_id: str, reason: str | None = None) -> None:
        body = self._to_json({"reason": reason or ""})
        self._execute_no_content(post_request(f"/v1/organizations/{organization_id}/suspend", body, False))

    def reactivate(self, organization_id: str) -> None:
        self._execute_no_content(post_request(f"/v1/organizations/{organization_id}/reactivate", None, False))

    def list_applications(self, organization_id: str) -> list[ApplicationResponse]:
        return self._execute_list(get_request(f"/v1/organizations/{organization_id}/applications"), map_application_response)

    def create_application(self, organization_id: str, name: str, idempotency_key: str | None = None) -> CreatedResourceResponse:
        request = post_request(f"/v1/organizations/{organization_id}/applications", self._to_json({"name": name}), False)
        request = request.with_header("Idempotency-Key", resolve_idempotency_key(idempotency_key))
        return self._execute(request, map_created_resource_response)
