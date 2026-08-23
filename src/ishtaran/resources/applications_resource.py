from __future__ import annotations

from .resource_support import ResourceSupport
from ..http.types import HttpTransport, post_request
from ..model.control_plane import CreatedResourceResponse, map_created_resource_response
from ..model.enum_factory import EnumValue


class ApplicationsResource(ResourceSupport):
    """Control Plane -- Applications (4 real routes, plus create in OrganizationsResource)."""

    def __init__(self, transport: HttpTransport) -> None:
        super().__init__(transport)

    def archive(self, application_id: str) -> None:
        self._execute_no_content(post_request(f"/v1/applications/{application_id}/archive", None, False))

    def suspend(self, application_id: str, reason: str | None = None) -> None:
        body = self._to_json({"reason": reason or ""})
        self._execute_no_content(post_request(f"/v1/applications/{application_id}/suspend", body, False))

    def reactivate(self, application_id: str) -> None:
        self._execute_no_content(post_request(f"/v1/applications/{application_id}/reactivate", None, False))

    def create_environment(self, application_id: str, environment_type: EnumValue[int]) -> CreatedResourceResponse:
        body = self._to_json({"type": environment_type.raw_value})
        return self._execute(post_request(f"/v1/applications/{application_id}/environments", body, False), map_created_resource_response)
