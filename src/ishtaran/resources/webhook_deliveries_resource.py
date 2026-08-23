from __future__ import annotations

from .resource_support import ResourceSupport
from ..http.types import HttpTransport, get_request, post_request
from ..model.webhook_endpoints import RedeliverWebhookResult, WebhookDeliveryResponse, map_redeliver_webhook_result, map_webhook_delivery_response


class WebhookDeliveriesResource(ResourceSupport):
    """Control Plane (management) -- WebhookDeliveries (2 real routes, same Notifications module)."""

    def __init__(self, transport: HttpTransport) -> None:
        super().__init__(transport)

    def get(self, webhook_delivery_id: str) -> WebhookDeliveryResponse:
        return self._execute(get_request(f"/v1/webhook-deliveries/{webhook_delivery_id}"), map_webhook_delivery_response)

    def redeliver(self, webhook_delivery_id: str) -> RedeliverWebhookResult:
        return self._execute(post_request(f"/v1/webhook-deliveries/{webhook_delivery_id}/redeliver", None, False), map_redeliver_webhook_result)
