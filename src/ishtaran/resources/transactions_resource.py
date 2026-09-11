from __future__ import annotations

from decimal import Decimal
from typing import Iterator
from urllib.parse import urlencode

from .resource_support import ResourceSupport
from ..http.types import HttpTransport, get_request, post_request
from ..idempotency.idempotency_key_generator import resolve_idempotency_key
from ..model.data_plane import (
    CreateTransactionResult,
    ExecutionResponse,
    ParticipantInput,
    TransactionResponse,
    TransactionStateResponse,
    map_create_transaction_result,
    map_execution_response,
    map_transaction_response,
    map_transaction_state_response,
)
from ..model.enum_factory import EnumValue
from ..model.enums import TransactionStatus
from ..pagination.page_iterator import paginate
from ..util.json_util import string_field_or_none
from ..util.polling import poll_until

_TERMINAL_STATUSES = {
    TransactionStatus.SETTLED.raw_value,  # type: ignore[attr-defined]
    TransactionStatus.REFUNDED.raw_value,  # type: ignore[attr-defined]
    TransactionStatus.CANCELLED.raw_value,  # type: ignore[attr-defined]
}


class TransactionsResource(ResourceSupport):
    """Data Plane -- Transactions (7 real routes)."""

    def __init__(self, transport: HttpTransport) -> None:
        super().__init__(transport)

    def create(
        self,
        organization_id: str,
        application_id: str,
        workflow_version_id: str | None,
        asset_network_id: str,
        amount: Decimal,
        participants: list[ParticipantInput],
        idempotency_key: str | None = None,
    ) -> CreateTransactionResult:
        key = resolve_idempotency_key(idempotency_key)
        body = self._to_json({
            "applicationId": application_id,
            "workflowVersionId": workflow_version_id,
            "assetNetworkId": asset_network_id,
            "amount": amount,
            "participants": [p.to_dict() for p in participants],
            "idempotencyKey": key,
        })
        return self._execute(post_request(f"/v1/organizations/{organization_id}/transactions", body, True), map_create_transaction_result)

    def get(self, transaction_id: str) -> TransactionResponse:
        return self._execute(get_request(f"/v1/transactions/{transaction_id}"), map_transaction_response)

    def get_state(self, transaction_id: str) -> TransactionStateResponse:
        return self._execute(get_request(f"/v1/transactions/{transaction_id}/state"), map_transaction_state_response)

    def reserve(self, transaction_id: str) -> str:
        return self._execute(
            post_request(f"/v1/transactions/{transaction_id}/reserve", None, True),
            lambda raw: string_field_or_none(raw, "entryGroupId") or "",
        )

    def cancel(self, transaction_id: str, reason: str | None = None) -> None:
        body = self._to_json({"reason": reason or ""})
        self._execute_no_content(post_request(f"/v1/transactions/{transaction_id}/cancel", body, False))

    def freeze(self, transaction_id: str, reason: str | None = None) -> None:
        body = self._to_json({"reason": reason or ""})
        self._execute_no_content(post_request(f"/v1/transactions/{transaction_id}/freeze", body, False))

    def unfreeze(self, transaction_id: str) -> None:
        self._execute_no_content(post_request(f"/v1/transactions/{transaction_id}/unfreeze", None, False))

    def search_executions(
        self,
        organization_id: str,
        status: EnumValue[int] | None = None,
        transaction_id: str | None = None,
        settlement_id: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
        skip: int | None = None,
        take: int | None = None,
    ) -> list[ExecutionResponse]:
        """
        PROMPT 5 section 9 (G.7) -- discoverability for outstanding/overdue Executions. The safety
        rule that makes an Organization settlement-restricted on an overdue Execution stays -- this
        closes the operational hole of finding which Execution caused it. Scoped by
        organization_id, same authorization model as every other
        /v1/organizations/{organization_id}/... route -- never cross-tenant. All string params go
        through urlencode, never concatenated raw (same discipline as list() above).
        """
        params: dict[str, str] = {}
        if status is not None:
            params["status"] = str(status.raw_value)
        if transaction_id is not None:
            params["transactionId"] = transaction_id
        if settlement_id is not None:
            params["settlementId"] = settlement_id
        if date_from is not None:
            params["from"] = date_from
        if date_to is not None:
            params["to"] = date_to
        if skip is not None:
            params["skip"] = str(skip)
        if take is not None:
            params["take"] = str(take)
        suffix = f"?{urlencode(params)}" if params else ""
        return self._execute_list(get_request(f"/v1/organizations/{organization_id}/executions{suffix}"), map_execution_response)

    def search_executions_all(
        self,
        organization_id: str,
        page_size: int,
        status: EnumValue[int] | None = None,
        transaction_id: str | None = None,
        settlement_id: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> Iterator[ExecutionResponse]:
        """Lazy iterator -- see SDK_CAPABILITY_SPEC.md section 12.7."""
        return paginate(
            page_size,
            lambda skip, take: self.search_executions(
                organization_id, status, transaction_id, settlement_id, date_from, date_to, skip, take,
            ),
        )

    def wait_for(self, transaction_id: str, timeout_seconds: float, poll_interval_seconds: float) -> TransactionResponse:
        """Safe polling, never infinite -- terminates at Settled/Refunded/Cancelled."""
        return poll_until(
            lambda: self.get(transaction_id),
            lambda r: r.status.raw_value in _TERMINAL_STATUSES,
            timeout_seconds,
            poll_interval_seconds,
            f"transaction_id={transaction_id}",
        )
