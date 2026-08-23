from __future__ import annotations

from .resource_support import ResourceSupport
from ..http.types import HttpTransport, get_request, post_request
from ..model.workflow import CreateEventTypeResult, EventTypeResponse, map_create_event_type_result, map_event_type_response


class EventTypesResource(ResourceSupport):
    """Data Plane -- EventTypes (2 real routes, same WorkflowRules module)."""

    def __init__(self, transport: HttpTransport) -> None:
        super().__init__(transport)

    def create(self, organization_id: str, name: str) -> CreateEventTypeResult:
        return self._execute(post_request(f"/v1/organizations/{organization_id}/event-types", self._to_json({"name": name}), False), map_create_event_type_result)

    def list(self, organization_id: str) -> list[EventTypeResponse]:
        return self._execute_list(get_request(f"/v1/organizations/{organization_id}/event-types"), map_event_type_response)
