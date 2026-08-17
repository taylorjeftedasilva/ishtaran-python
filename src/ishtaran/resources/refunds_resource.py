from __future__ import annotations

from decimal import Decimal

from .resource_support import ResourceSupport
from ..http.types import HttpTransport, get_request, post_request
from ..idempotency.idempotency_key_generator import resolve_idempotency_key
from ..model.settlement import ExecuteRefundResult, RefundResponse, map_execute_refund_result, map_refund_response


class RefundsResource(ResourceSupport):
    """Data Plane -- Refunds (3 rotas reais, sob o mesmo modulo real Settlement)."""

    def __init__(self, transport: HttpTransport) -> None:
        super().__init__(transport)

    def execute_refund(
        self, transaction_id: str, amount: Decimal | None = None, reason: str | None = None, idempotency_key: str | None = None,
    ) -> ExecuteRefundResult:
        """amount None = reembolso total."""
        body = self._to_json({"amount": amount, "reason": reason, "idempotencyKey": resolve_idempotency_key(idempotency_key)})
        return self._execute(post_request(f"/v1/transactions/{transaction_id}/refunds", body, True), map_execute_refund_result)

    def list_by_transaction(self, transaction_id: str) -> list[RefundResponse]:
        return self._execute_list(get_request(f"/v1/transactions/{transaction_id}/refunds"), map_refund_response)

    def get(self, refund_id: str) -> RefundResponse:
        return self._execute(get_request(f"/v1/refunds/{refund_id}"), map_refund_response)
