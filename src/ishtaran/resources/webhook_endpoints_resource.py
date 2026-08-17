from __future__ import annotations

from typing import List
from urllib.parse import urlencode

from .resource_support import ResourceSupport
from ..http.types import HttpTransport, get_request, post_request
from ..model.enum_factory import EnumValue
from ..model.webhook_endpoints import (
    ConfigureWebhookEndpointResult,
    RotateWebhookEndpointSecretResult,
    WebhookDeliveryResponse,
    WebhookEndpointResponse,
    map_configure_webhook_endpoint_result,
    map_rotate_webhook_endpoint_secret_result,
    map_webhook_delivery_response,
    map_webhook_endpoint_response,
)


class WebhookEndpointsResource(ResourceSupport):
    """
    Control Plane (gestao) -- WebhookEndpoints (6 rotas reais). Sempre Member JWT -- nao aceita API
    Key hoje (Known Gap real, ver SDK_CAPABILITY_SPEC.md secao 12.4).
    """

    def __init__(self, transport: HttpTransport) -> None:
        super().__init__(transport)

    def create(self, organization_id: str, url: str) -> ConfigureWebhookEndpointResult:
        """secret so e retornado aqui -- guarde-o imediatamente, nunca recuperavel depois."""
        return self._execute(post_request(f"/v1/organizations/{organization_id}/webhook-endpoints", self._to_json({"url": url}), False), map_configure_webhook_endpoint_result)

    # typing.List (nao list[...]) -- o metodo `list` abaixo shadowaria o builtin `list` em
    # qualquer anotacao subsequente no corpo desta classe (bug real encontrado via mypy).
    def list(self, organization_id: str) -> List[WebhookEndpointResponse]:
        return self._execute_list(get_request(f"/v1/organizations/{organization_id}/webhook-endpoints"), map_webhook_endpoint_response)

    def get(self, webhook_endpoint_id: str) -> WebhookEndpointResponse:
        return self._execute(get_request(f"/v1/webhook-endpoints/{webhook_endpoint_id}"), map_webhook_endpoint_response)

    def rotate_secret(self, webhook_endpoint_id: str) -> RotateWebhookEndpointSecretResult:
        """Novo secret -- o anterior deixa de validar assinaturas imediatamente."""
        return self._execute(post_request(f"/v1/webhook-endpoints/{webhook_endpoint_id}/rotate-secret", None, False), map_rotate_webhook_endpoint_secret_result)

    def deactivate(self, webhook_endpoint_id: str) -> None:
        self._execute_no_content(post_request(f"/v1/webhook-endpoints/{webhook_endpoint_id}/deactivate", None, False))

    def list_deliveries(
        self, webhook_endpoint_id: str, event_type: str | None = None, status: EnumValue[int] | None = None,
    ) -> List[WebhookDeliveryResponse]:
        """
        status e enviado como NOME (string, case-insensitive) na query string -- diferente do
        filtro de AssetNetworkCatalog (inteiro). Confirmado em codigo-fonte:
        Enum.Parse<WebhookDeliveryStatus>(status, ignoreCase: true).
        """
        params: dict[str, str] = {}
        if event_type is not None:
            params["eventType"] = event_type
        if status is not None:
            params["status"] = status.name
        suffix = f"?{urlencode(params)}" if params else ""
        return self._execute_list(get_request(f"/v1/webhook-endpoints/{webhook_endpoint_id}/deliveries{suffix}"), map_webhook_delivery_response)
