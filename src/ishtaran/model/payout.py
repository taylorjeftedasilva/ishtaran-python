from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from .enum_factory import EnumValue
from .enums import PayoutBatchObligationStatus, PayoutBatchStatus, PayoutBatchTrigger
from ..util.json_util import array_field, field, money, string_field, string_field_or_none


@dataclass(frozen=True)
class PayableSummaryResponse:
    """
    SPEC-024 BL-PAY-004/BR-PAY-002 -- "a receber" per beneficiary, never confused with the
    Account's on-chain (Available) balance. accrued = sum of Payable; reserved_for_payout = sum
    of open PayoutBatches; paid = cumulative delivered history (never confused with Available).
    """

    accrued: Decimal
    reserved_for_payout: Decimal
    paid: Decimal


def map_payable_summary_response(raw: Any) -> PayableSummaryResponse:
    return PayableSummaryResponse(
        accrued=money(field(raw, "accrued")),
        reserved_for_payout=money(field(raw, "reservedForPayout")),
        paid=money(field(raw, "paid")),
    )


@dataclass(frozen=True)
class PayoutBatchSourceObligationResponse:
    origin_reference: str
    amount: Decimal


def _map_payout_batch_source_obligation_response(raw: Any) -> PayoutBatchSourceObligationResponse:
    return PayoutBatchSourceObligationResponse(
        origin_reference=string_field(raw, "originReference"),
        amount=money(field(raw, "amount")),
    )


@dataclass(frozen=True)
class PayoutBatchObligationResponse:
    owner_id: str
    amount: Decimal
    source_obligations: list[PayoutBatchSourceObligationResponse]
    destination_address: str
    status: EnumValue[int]


def _map_payout_batch_obligation_response(raw: Any) -> PayoutBatchObligationResponse:
    return PayoutBatchObligationResponse(
        owner_id=string_field(raw, "ownerId"),
        amount=money(field(raw, "amount")),
        source_obligations=array_field(raw, "sourceObligations", _map_payout_batch_source_obligation_response),
        destination_address=string_field(raw, "destinationAddress"),
        status=PayoutBatchObligationStatus.from_raw(int(field(raw, "status"))),
    )


@dataclass(frozen=True)
class NetworkExecutionQuoteSnapshotResponse:
    """SPEC-025 Descoberta 6/7 -- always the frozen copy captured at reservation time, never recomputed/reread on every read."""

    network: str
    native_execution_cost: Decimal
    resource_asset_network_id: str | None
    quote_currency: str
    fx: Decimal
    total_charged: Decimal
    authorized_native_cost: Decimal
    expires_at: str


def _map_network_execution_quote_snapshot_response(raw: Any) -> NetworkExecutionQuoteSnapshotResponse:
    return NetworkExecutionQuoteSnapshotResponse(
        network=string_field(raw, "network"),
        native_execution_cost=money(field(raw, "nativeExecutionCost")),
        resource_asset_network_id=string_field_or_none(raw, "resourceAssetNetworkId"),
        quote_currency=string_field(raw, "quoteCurrency"),
        fx=money(field(raw, "fx")),
        total_charged=money(field(raw, "totalCharged")),
        authorized_native_cost=money(field(raw, "authorizedNativeCost")),
        expires_at=string_field(raw, "expiresAt"),
    )


@dataclass(frozen=True)
class PayoutBatchResponse:
    """
    SPEC-025 -- a batched payout execution grouping N beneficiary obligations under a single
    NetworkExecutionQuote. This SDK slice only ever creates batches with trigger = MANUAL (the
    public route accepts no other trigger yet -- THRESHOLD_CROSSED/SCHEDULED exist in the domain
    but aren't reachable through the public API today).
    """

    payout_batch_id: str
    organization_id: str
    environment_id: str
    asset_network_id: str
    trigger: EnumValue[int]
    status: EnumValue[int]
    obligations: list[PayoutBatchObligationResponse]
    network_execution_quote_snapshot: NetworkExecutionQuoteSnapshotResponse
    signing_request_id: str | None
    created_at: str


def map_payout_batch_response(raw: Any) -> PayoutBatchResponse:
    return PayoutBatchResponse(
        payout_batch_id=string_field(raw, "payoutBatchId"),
        organization_id=string_field(raw, "organizationId"),
        environment_id=string_field(raw, "environmentId"),
        asset_network_id=string_field(raw, "assetNetworkId"),
        trigger=PayoutBatchTrigger.from_raw(int(field(raw, "trigger"))),
        status=PayoutBatchStatus.from_raw(int(field(raw, "status"))),
        obligations=array_field(raw, "obligations", _map_payout_batch_obligation_response),
        network_execution_quote_snapshot=_map_network_execution_quote_snapshot_response(field(raw, "networkExecutionQuoteSnapshot")),
        signing_request_id=string_field_or_none(raw, "signingRequestId"),
        created_at=string_field(raw, "createdAt"),
    )


@dataclass(frozen=True)
class CreatePayoutBatchResult:
    """payout_batch_id is None when there were no eligible candidates (204 No Content, a legitimate no-op -- never an error)."""

    payout_batch_id: str | None
