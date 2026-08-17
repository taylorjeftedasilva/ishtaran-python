from __future__ import annotations

from .resource_support import ResourceSupport
from ..http.types import HttpTransport, get_request, post_request
from ..idempotency.idempotency_key_generator import resolve_idempotency_key
from ..model.settlement import (
    ExecuteSettlementResult,
    SettlementResponse,
    TransactionSettlementSummaryResponse,
    map_execute_settlement_result,
    map_settlement_response,
    map_transaction_settlement_summary_response,
)


class SettlementsResource(ResourceSupport):
    """Data Plane -- Settlement (5 rotas reais; Refunds em RefundsResource)."""

    def __init__(self, transport: HttpTransport) -> None:
        super().__init__(transport)

    def execute_settlement(self, transaction_id: str, idempotency_key: str | None = None) -> ExecuteSettlementResult:
        body = self._to_json({"idempotencyKey": resolve_idempotency_key(idempotency_key)})
        return self._execute(post_request(f"/v1/transactions/{transaction_id}/settlements", body, True), map_execute_settlement_result)

    def list_by_transaction(self, transaction_id: str) -> list[SettlementResponse]:
        return self._execute_list(get_request(f"/v1/transactions/{transaction_id}/settlements"), map_settlement_response)

    def get(self, settlement_id: str) -> SettlementResponse:
        return self._execute(get_request(f"/v1/settlements/{settlement_id}"), map_settlement_response)

    def get_summary(self, transaction_id: str) -> TransactionSettlementSummaryResponse:
        return self._execute(get_request(f"/v1/transactions/{transaction_id}/settlement-summary"), map_transaction_settlement_summary_response)

    def release_retained_split(self, settlement_id: str, allocation_id: str, idempotency_key: str | None = None) -> None:
        body = self._to_json({"idempotencyKey": resolve_idempotency_key(idempotency_key)})
        self._execute_no_content(post_request(f"/v1/settlements/{settlement_id}/split-allocations/{allocation_id}/release", body, True))
