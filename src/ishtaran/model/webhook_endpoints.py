from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .enum_factory import EnumValue
from .enums import WebhookDeliveryStatus, WebhookEndpointStatus
from ..util.json_util import field, string_field, string_field_or_none


@dataclass(frozen=True)
class WebhookEndpointResponse:
    webhook_endpoint_id: str
    organization_id: str
    url: str | None
    status: EnumValue[int]
    created_at: str


def map_webhook_endpoint_response(raw: Any) -> WebhookEndpointResponse:
    return WebhookEndpointResponse(
        webhook_endpoint_id=string_field(raw, "webhookEndpointId"),
        organization_id=string_field(raw, "organizationId"),
        url=string_field_or_none(raw, "url"),
        status=WebhookEndpointStatus.from_raw(int(field(raw, "status"))),
        created_at=string_field(raw, "createdAt"),
    )


@dataclass(frozen=True)
class WebhookDeliveryResponse:
    webhook_delivery_id: str
    webhook_endpoint_id: str
    event_type: str | None
    # sequenceNumber e int64 -- str preserva precisao mesmo alem de valores seguros de int nativo
    # (Python int e arbitrary-precision, entao aqui e so por paridade conceitual com TS/Java).
    sequence_number: str
    status: EnumValue[int]
    attempt_count: int
    max_attempts: int
    next_attempt_at: str | None
    last_attempt_at: str | None
    last_error: str | None
    redelivered_from_id: str | None
    created_at: str


def map_webhook_delivery_response(raw: Any) -> WebhookDeliveryResponse:
    return WebhookDeliveryResponse(
        webhook_delivery_id=string_field(raw, "webhookDeliveryId"),
        webhook_endpoint_id=string_field(raw, "webhookEndpointId"),
        event_type=string_field_or_none(raw, "eventType"),
        sequence_number=str(field(raw, "sequenceNumber")),
        status=WebhookDeliveryStatus.from_raw(int(field(raw, "status"))),
        attempt_count=int(field(raw, "attemptCount")),
        max_attempts=int(field(raw, "maxAttempts")),
        next_attempt_at=string_field_or_none(raw, "nextAttemptAt"),
        last_attempt_at=string_field_or_none(raw, "lastAttemptAt"),
        last_error=string_field_or_none(raw, "lastError"),
        redelivered_from_id=string_field_or_none(raw, "redeliveredFromId"),
        created_at=string_field(raw, "createdAt"),
    )


@dataclass(frozen=True)
class ConfigureWebhookEndpointResult:
    webhook_endpoint_id: str
    secret: str | None


def map_configure_webhook_endpoint_result(raw: Any) -> ConfigureWebhookEndpointResult:
    return ConfigureWebhookEndpointResult(
        webhook_endpoint_id=string_field(raw, "webhookEndpointId"),
        secret=string_field_or_none(raw, "secret"),
    )


@dataclass(frozen=True)
class RotateWebhookEndpointSecretResult:
    webhook_endpoint_id: str
    secret: str | None


def map_rotate_webhook_endpoint_secret_result(raw: Any) -> RotateWebhookEndpointSecretResult:
    return RotateWebhookEndpointSecretResult(
        webhook_endpoint_id=string_field(raw, "webhookEndpointId"),
        secret=string_field_or_none(raw, "secret"),
    )


@dataclass(frozen=True)
class RedeliverWebhookResult:
    webhook_delivery_id: str


def map_redeliver_webhook_result(raw: Any) -> RedeliverWebhookResult:
    return RedeliverWebhookResult(webhook_delivery_id=string_field(raw, "webhookDeliveryId"))
