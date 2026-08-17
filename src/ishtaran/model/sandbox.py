from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from ..util.json_util import field, money, safe_int_or_none, string_field, string_field_or_none


@dataclass(frozen=True)
class SandboxObservedAddressResponse:
    sandbox_observed_address_id: str
    address: str | None
    asset_network_id: str
    last_observed_reference: str | None
    last_confirmation_count: int | None
    created_at: str


def map_sandbox_observed_address_response(raw: Any) -> SandboxObservedAddressResponse:
    return SandboxObservedAddressResponse(
        sandbox_observed_address_id=string_field(raw, "sandboxObservedAddressId"),
        address=string_field_or_none(raw, "address"),
        asset_network_id=string_field(raw, "assetNetworkId"),
        last_observed_reference=string_field_or_none(raw, "lastObservedReference"),
        last_confirmation_count=safe_int_or_none(field(raw, "lastConfirmationCount")),
        created_at=string_field(raw, "createdAt"),
    )


@dataclass(frozen=True)
class SandboxBroadcastAttemptResponse:
    sandbox_broadcast_attempt_id: str
    destination_address: str | None
    amount: Decimal
    asset_network_id: str
    status: str | None
    technical_reference: str | None
    created_at: str


def map_sandbox_broadcast_attempt_response(raw: Any) -> SandboxBroadcastAttemptResponse:
    return SandboxBroadcastAttemptResponse(
        sandbox_broadcast_attempt_id=string_field(raw, "sandboxBroadcastAttemptId"),
        destination_address=string_field_or_none(raw, "destinationAddress"),
        amount=money(field(raw, "amount")),
        asset_network_id=string_field(raw, "assetNetworkId"),
        status=string_field_or_none(raw, "status"),
        technical_reference=string_field_or_none(raw, "technicalReference"),
        created_at=string_field(raw, "createdAt"),
    )


@dataclass(frozen=True)
class SandboxTreasuryObservedBalanceResponse:
    asset_network_id: str
    balance: Decimal
    updated_at: str


def map_sandbox_treasury_observed_balance_response(raw: Any) -> SandboxTreasuryObservedBalanceResponse:
    return SandboxTreasuryObservedBalanceResponse(
        asset_network_id=string_field(raw, "assetNetworkId"),
        balance=money(field(raw, "balance")),
        updated_at=string_field(raw, "updatedAt"),
    )


@dataclass(frozen=True)
class SandboxObservedAddressResult:
    sandbox_observed_address_id: str


def map_sandbox_observed_address_result(raw: Any) -> SandboxObservedAddressResult:
    return SandboxObservedAddressResult(sandbox_observed_address_id=string_field(raw, "sandboxObservedAddressId"))


@dataclass(frozen=True)
class SandboxBroadcastAttemptResult:
    sandbox_broadcast_attempt_id: str


def map_sandbox_broadcast_attempt_result(raw: Any) -> SandboxBroadcastAttemptResult:
    return SandboxBroadcastAttemptResult(sandbox_broadcast_attempt_id=string_field(raw, "sandboxBroadcastAttemptId"))
