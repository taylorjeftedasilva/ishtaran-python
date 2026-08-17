from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from .enum_factory import EnumValue
from .enums import DepositStatus, PaymentIntentStatus
from ..util.json_util import array_field, field, money, string_field, string_field_or_none


@dataclass(frozen=True)
class DepositResponse:
    deposit_id: str
    payment_intent_id: str
    technical_reference: str | None
    amount: Decimal
    status: EnumValue[int]
    confirmation_count: int
    was_confirmed_before_reorg: bool
    is_late: bool
    created_at: str


def map_deposit_response(raw: Any) -> DepositResponse:
    return DepositResponse(
        deposit_id=string_field(raw, "depositId"),
        payment_intent_id=string_field(raw, "paymentIntentId"),
        technical_reference=string_field_or_none(raw, "technicalReference"),
        amount=money(field(raw, "amount")),
        status=DepositStatus.from_raw(int(field(raw, "status"))),
        confirmation_count=int(field(raw, "confirmationCount")),
        was_confirmed_before_reorg=bool(field(raw, "wasConfirmedBeforeReorg")),
        is_late=bool(field(raw, "isLate")),
        created_at=string_field(raw, "createdAt"),
    )


@dataclass(frozen=True)
class PaymentIntentResponse:
    payment_intent_id: str
    organization_id: str
    transaction_id: str
    asset_network_id: str
    amount: Decimal
    status: EnumValue[int]
    expires_at: str | None
    deposit_address: str | None
    deposits: list[DepositResponse]
    created_at: str


def map_payment_intent_response(raw: Any) -> PaymentIntentResponse:
    return PaymentIntentResponse(
        payment_intent_id=string_field(raw, "paymentIntentId"),
        organization_id=string_field(raw, "organizationId"),
        transaction_id=string_field(raw, "transactionId"),
        asset_network_id=string_field(raw, "assetNetworkId"),
        amount=money(field(raw, "amount")),
        status=PaymentIntentStatus.from_raw(int(field(raw, "status"))),
        expires_at=string_field_or_none(raw, "expiresAt"),
        deposit_address=string_field_or_none(raw, "depositAddress"),
        deposits=array_field(raw, "deposits", map_deposit_response),
        created_at=string_field(raw, "createdAt"),
    )


@dataclass(frozen=True)
class CreatePaymentIntentResult:
    payment_intent_id: str


def map_create_payment_intent_result(raw: Any) -> CreatePaymentIntentResult:
    return CreatePaymentIntentResult(payment_intent_id=string_field(raw, "paymentIntentId"))
