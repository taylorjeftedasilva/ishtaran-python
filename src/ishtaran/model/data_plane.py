from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from .enum_factory import EnumValue
from .enums import EntryNature, TransactionStatus, WithdrawalStatus
from ..util.json_util import array_field, field, money, string_field, string_field_or_none


@dataclass(frozen=True)
class AccountResponse:
    account_id: str
    organization_id: str
    external_id: str | None
    status: str | None
    created_at: str
    authorized_application_ids: list[str] | None


def map_account_response(raw: Any) -> AccountResponse:
    ids = field(raw, "authorizedApplicationIds")
    return AccountResponse(
        account_id=string_field(raw, "accountId"),
        organization_id=string_field(raw, "organizationId"),
        external_id=string_field_or_none(raw, "externalId"),
        status=string_field_or_none(raw, "status"),
        created_at=string_field(raw, "createdAt"),
        authorized_application_ids=None if ids is None else [str(x) for x in ids],
    )


@dataclass(frozen=True)
class CreateAccountResult:
    account_id: str


def map_create_account_result(raw: Any) -> CreateAccountResult:
    return CreateAccountResult(account_id=string_field(raw, "accountId"))


@dataclass(frozen=True)
class WithdrawalQuoteResponse:
    account_id: str
    withdrawal_destination_id: str
    asset_network_id: str
    requested_amount: Decimal
    estimated_network_fee: Decimal
    estimated_recipient_amount: Decimal
    expires_at: str


def map_withdrawal_quote_response(raw: Any) -> WithdrawalQuoteResponse:
    return WithdrawalQuoteResponse(
        account_id=string_field(raw, "accountId"),
        withdrawal_destination_id=string_field(raw, "withdrawalDestinationId"),
        asset_network_id=string_field(raw, "assetNetworkId"),
        requested_amount=money(field(raw, "requestedAmount")),
        estimated_network_fee=money(field(raw, "estimatedNetworkFee")),
        estimated_recipient_amount=money(field(raw, "estimatedRecipientAmount")),
        expires_at=string_field(raw, "expiresAt"),
    )


@dataclass(frozen=True)
class WithdrawalResponse:
    withdrawal_id: str
    organization_id: str
    account_id: str
    withdrawal_destination_id: str
    asset_network_id: str
    amount: Decimal
    estimated_network_fee: Decimal
    estimated_recipient_amount: Decimal
    final_network_fee: Decimal | None
    final_recipient_amount: Decimal | None
    status: EnumValue[int]
    entry_group_id: str | None
    technical_reference: str | None
    created_at: str


def map_withdrawal_response(raw: Any) -> WithdrawalResponse:
    final_fee = field(raw, "finalNetworkFee")
    final_amount = field(raw, "finalRecipientAmount")
    return WithdrawalResponse(
        withdrawal_id=string_field(raw, "withdrawalId"),
        organization_id=string_field(raw, "organizationId"),
        account_id=string_field(raw, "accountId"),
        withdrawal_destination_id=string_field(raw, "withdrawalDestinationId"),
        asset_network_id=string_field(raw, "assetNetworkId"),
        amount=money(field(raw, "amount")),
        estimated_network_fee=money(field(raw, "estimatedNetworkFee")),
        estimated_recipient_amount=money(field(raw, "estimatedRecipientAmount")),
        final_network_fee=None if final_fee is None else money(final_fee),
        final_recipient_amount=None if final_amount is None else money(final_amount),
        status=WithdrawalStatus.from_raw(int(field(raw, "status"))),
        entry_group_id=string_field_or_none(raw, "entryGroupId"),
        technical_reference=string_field_or_none(raw, "technicalReference"),
        created_at=string_field(raw, "createdAt"),
    )


@dataclass(frozen=True)
class CreateWithdrawalDestinationResult:
    withdrawal_destination_id: str


def map_create_withdrawal_destination_result(raw: Any) -> CreateWithdrawalDestinationResult:
    return CreateWithdrawalDestinationResult(withdrawal_destination_id=string_field(raw, "withdrawalDestinationId"))


@dataclass(frozen=True)
class BalanceResponse:
    available: Decimal
    pending: Decimal
    reserved: Decimal


def map_balance_response(raw: Any) -> BalanceResponse:
    return BalanceResponse(
        available=money(field(raw, "available")),
        pending=money(field(raw, "pending")),
        reserved=money(field(raw, "reserved")),
    )


@dataclass(frozen=True)
class LedgerEntryResponse:
    entry_id: str
    ledger_account_id: str
    entry_group_id: str
    nature: EnumValue[int]
    amount: Decimal
    origin_reference: str
    reversal_of_entry_group_id: str | None
    created_at: str


def map_ledger_entry_response(raw: Any) -> LedgerEntryResponse:
    return LedgerEntryResponse(
        entry_id=string_field(raw, "entryId"),
        ledger_account_id=string_field(raw, "ledgerAccountId"),
        entry_group_id=string_field(raw, "entryGroupId"),
        nature=EntryNature.from_raw(int(field(raw, "nature"))),
        amount=money(field(raw, "amount")),
        origin_reference=string_field(raw, "originReference"),
        reversal_of_entry_group_id=string_field_or_none(raw, "reversalOfEntryGroupId"),
        created_at=string_field(raw, "createdAt"),
    )


@dataclass(frozen=True)
class ParticipantInput:
    account_id: str
    role: str
    is_payer: bool
    split_percentage: Decimal | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "accountId": self.account_id,
            "role": self.role,
            "isPayer": self.is_payer,
            "splitPercentage": self.split_percentage,
        }


@dataclass(frozen=True)
class TransactionResponse:
    transaction_id: str
    organization_id: str
    application_id: str
    workflow_version_id: str | None
    current_workflow_state_id: str | None
    asset_network_id: str
    amount: Decimal
    status: EnumValue[int]
    payer_account_id: str
    participants: list[Any]
    created_at: str
    settled_amount: Decimal
    refunded_amount: Decimal


def map_transaction_response(raw: Any) -> TransactionResponse:
    return TransactionResponse(
        transaction_id=string_field(raw, "transactionId"),
        organization_id=string_field(raw, "organizationId"),
        application_id=string_field(raw, "applicationId"),
        workflow_version_id=string_field_or_none(raw, "workflowVersionId"),
        current_workflow_state_id=string_field_or_none(raw, "currentWorkflowStateId"),
        asset_network_id=string_field(raw, "assetNetworkId"),
        amount=money(field(raw, "amount")),
        status=TransactionStatus.from_raw(int(field(raw, "status"))),
        payer_account_id=string_field(raw, "payerAccountId"),
        participants=array_field(raw, "participants", lambda x: x),
        created_at=string_field(raw, "createdAt"),
        settled_amount=money(field(raw, "settledAmount")),
        refunded_amount=money(field(raw, "refundedAmount")),
    )


@dataclass(frozen=True)
class CreateTransactionResult:
    transaction_id: str


def map_create_transaction_result(raw: Any) -> CreateTransactionResult:
    return CreateTransactionResult(transaction_id=string_field(raw, "transactionId"))


@dataclass(frozen=True)
class TransactionStateResponse:
    status: EnumValue[int]
    workflow_version_id: str | None
    current_workflow_state_id: str | None


def map_transaction_state_response(raw: Any) -> TransactionStateResponse:
    return TransactionStateResponse(
        status=TransactionStatus.from_raw(int(field(raw, "status"))),
        workflow_version_id=string_field_or_none(raw, "workflowVersionId"),
        current_workflow_state_id=string_field_or_none(raw, "currentWorkflowStateId"),
    )
