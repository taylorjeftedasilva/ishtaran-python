import json

from ishtaran.model.enums import WebhookDeliveryStatus
from ishtaran.resources.webhook_endpoints_resource import WebhookEndpointsResource
from .fake_transport import FakeHttpTransport


def test_list_deliveries_status_sent_as_string_name_not_integer() -> None:
    fake = FakeHttpTransport().enqueue(FakeHttpTransport.json(200, "[]"))
    resource = WebhookEndpointsResource(fake)

    resource.list_deliveries("ep-1", status=WebhookDeliveryStatus.DELIVERED)  # type: ignore[attr-defined]

    assert "status=DELIVERED" in fake.received[0].path


def test_list_deliveries_event_type_is_url_encoded_never_injects_extra_params() -> None:
    fake = FakeHttpTransport().enqueue(FakeHttpTransport.json(200, "[]"))
    resource = WebhookEndpointsResource(fake)

    resource.list_deliveries("ep-1", event_type="payment.received&status=DELIVERED")

    path = fake.received[0].path
    assert "eventType=payment.received%26status%3DDELIVERED" in path


def test_create_exposes_secret_only_once() -> None:
    body = json.dumps({"webhookEndpointId": "ep-1", "secret": "whsec_abc123"})
    fake = FakeHttpTransport().enqueue(FakeHttpTransport.json(201, body))
    resource = WebhookEndpointsResource(fake)

    result = resource.create("org-1", "https://example.com/webhook")

    assert result.webhook_endpoint_id == "ep-1"
    assert result.secret == "whsec_abc123"
