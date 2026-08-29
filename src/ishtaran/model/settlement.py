from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from .enum_factory import EnumValue
from .enums import RefundStatus, SettlementStatus, SplitAllocationStatus, SplitRetentionReason
from ..util.json_util import array_field, field, money, string_field, string_field_or_none


@dataclass(frozen=True)
class SettlementSplitAllocationResponse:
    split_allocation_id: str
    participant_id: str
    account_id: str
    amount: Decimal
    status: EnumValue[int]
    retention_reason: EnumValue[int] | None
    released_at: str | None


def _map_split_allocation(raw: Any) -> SettlementSplitAllocationResponse:
    retention_reason_raw = field(raw, "retentionReason")
    return SettlementSplitAllocationResponse(
        split_allocation_id=string_field(raw, "splitAllocationId"),
        participant_id=string_field(raw, "participantId"),
        account_id=string_field(raw, "accountId"),
        amount=money(field(raw, "amount")),
        status=SplitAllocationStatus.from_raw(int(field(raw, "status"))),
        retention_reason=None if retention_reason_raw is None else SplitRetentionReason.from_raw(int(retention_reason_raw)),
        released_at=string_field_or_none(raw, "releasedAt"),
    )


@dataclass(frozen=True)
class SettlementResponse:
    settlement_id: str
    transaction_id: str
    organization_id: str
    application_id: str
    asset_network_id: str
    gross_amount: Decimal
    platform_fee_amount: Decimal
    distributable_amount: Decimal
    fee_percentage_applied: Decimal
    platform_revenue_account_id: str
    pricing_policy_id: str
    status: EnumValue[int]
    entry_group_id: str | None
    # DEC-037 -- populated only under SelfCustody, once SelfCustodySettlementExecutionStrategy
    # creates a real SigningRequest (never under ManagedCustody, never before there's something to
    # sign). Fetch it via client.signing_requests.get(signing_request_id) to sign locally.
    signing_request_id: str | None
    split_allocations: list[SettlementSplitAllocationResponse]
    created_at: str
    executed_at: str | None


def map_settlement_response(raw: Any) -> SettlementResponse:
    return SettlementResponse(
        settlement_id=string_field(raw, "settlementId"),
        transaction_id=string_field(raw, "transactionId"),
        organization_id=string_field(raw, "organizationId"),
        application_id=string_field(raw, "applicationId"),
        asset_network_id=string_field(raw, "assetNetworkId"),
        gross_amount=money(field(raw, "grossAmount")),
        platform_fee_amount=money(field(raw, "platformFeeAmount")),
        distributable_amount=money(field(raw, "distributableAmount")),
        fee_percentage_applied=money(field(raw, "feePercentageApplied")),
        platform_revenue_account_id=string_field(raw, "platformRevenueAccountId"),
        pricing_policy_id=string_field(raw, "pricingPolicyId"),
        status=SettlementStatus.from_raw(int(field(raw, "status"))),
        entry_group_id=string_field_or_none(raw, "entryGroupId"),
        signing_request_id=string_field_or_none(raw, "signingRequestId"),
        split_allocations=array_field(raw, "splitAllocations", _map_split_allocation),
        created_at=string_field(raw, "createdAt"),
        executed_at=string_field_or_none(raw, "executedAt"),
    )


@dataclass(frozen=True)
class RefundResponse:
    refund_id: str
    transaction_id: str
    organization_id: str
    amount: Decimal
    reason: str | None
    status: EnumValue[int]
    entry_group_id: str | None
    created_at: str
    executed_at: str | None


def map_refund_response(raw: Any) -> RefundResponse:
    return RefundResponse(
        refund_id=string_field(raw, "refundId"),
        transaction_id=string_field(raw, "transactionId"),
        organization_id=string_field(raw, "organizationId"),
        amount=money(field(raw, "amount")),
        reason=string_field_or_none(raw, "reason"),
        status=RefundStatus.from_raw(int(field(raw, "status"))),
        entry_group_id=string_field_or_none(raw, "entryGroupId"),
        created_at=string_field(raw, "createdAt"),
        executed_at=string_field_or_none(raw, "executedAt"),
    )


@dataclass(frozen=True)
class TransactionSettlementSummaryResponse:
    transaction_id: str
    settled_amount: Decimal
    refunded_amount: Decimal
    remaining_reserved_amount: Decimal
    retained_amount: Decimal


def map_transaction_settlement_summary_response(raw: Any) -> TransactionSettlementSummaryResponse:
    return TransactionSettlementSummaryResponse(
        transaction_id=string_field(raw, "transactionId"),
        settled_amount=money(field(raw, "settledAmount")),
        refunded_amount=money(field(raw, "refundedAmount")),
        remaining_reserved_amount=money(field(raw, "remainingReservedAmount")),
        retained_amount=money(field(raw, "retainedAmount")),
    )


@dataclass(frozen=True)
class ExecuteSettlementResult:
    settlement_id: str


def map_execute_settlement_result(raw: Any) -> ExecuteSettlementResult:
    return ExecuteSettlementResult(settlement_id=string_field(raw, "settlementId"))


@dataclass(frozen=True)
class ExecuteRefundResult:
    refund_id: str


def map_execute_refund_result(raw: Any) -> ExecuteRefundResult:
    return ExecuteRefundResult(refund_id=string_field(raw, "refundId"))
