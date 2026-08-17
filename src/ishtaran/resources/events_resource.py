from __future__ import annotations

from .resource_support import ResourceSupport
from ..http.types import HttpTransport, post_request
from ..idempotency.idempotency_key_generator import resolve_idempotency_key
from ..model.enum_factory import EnumValue
from ..model.workflow import EventIngestionResult, map_event_ingestion_result


class EventsResource(ResourceSupport):
    """Data Plane -- Events (1 rota real: ingestao, mesmo modulo WorkflowRules)."""

    def __init__(self, transport: HttpTransport) -> None:
        super().__init__(transport)

    def ingest(
        self,
        application_id: str,
        workflow_version_id: str,
        current_state_id: str,
        transaction_reference: str,
        event_type_id: str,
        event_source: EnumValue[int],
        payload: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> EventIngestionResult:
        body = self._to_json({
            "workflowVersionId": workflow_version_id, "currentStateId": current_state_id,
            "transactionReference": transaction_reference, "eventTypeId": event_type_id,
            "idempotencyKey": resolve_idempotency_key(idempotency_key),
            "payload": payload, "eventSource": event_source.raw_value,
        })
        return self._execute(post_request(f"/v1/applications/{application_id}/events", body, True), map_event_ingestion_result)
