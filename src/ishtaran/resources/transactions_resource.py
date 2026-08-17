from __future__ import annotations

from decimal import Decimal

from .resource_support import ResourceSupport
from ..http.types import HttpTransport, get_request, post_request
from ..idempotency.idempotency_key_generator import resolve_idempotency_key
from ..model.data_plane import (
    CreateTransactionResult,
    ParticipantInput,
    TransactionResponse,
    TransactionStateResponse,
    map_create_transaction_result,
    map_transaction_response,
    map_transaction_state_response,
)
from ..model.enums import TransactionStatus
from ..util.json_util import string_field_or_none
from ..util.polling import poll_until

_TERMINAL_STATUSES = {
    TransactionStatus.SETTLED.raw_value,  # type: ignore[attr-defined]
    TransactionStatus.REFUNDED.raw_value,  # type: ignore[attr-defined]
    TransactionStatus.CANCELLED.raw_value,  # type: ignore[attr-defined]
}


class TransactionsResource(ResourceSupport):
    """Data Plane -- Transactions (7 rotas reais)."""

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

    def wait_for(self, transaction_id: str, timeout_seconds: float, poll_interval_seconds: float) -> TransactionResponse:
        """Polling seguro, nunca infinito -- termina em Settled/Refunded/Cancelled."""
        return poll_until(
            lambda: self.get(transaction_id),
            lambda r: r.status.raw_value in _TERMINAL_STATUSES,
            timeout_seconds,
            poll_interval_seconds,
            f"transaction_id={transaction_id}",
        )
