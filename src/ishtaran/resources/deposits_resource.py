from __future__ import annotations

from decimal import Decimal

from .resource_support import ResourceSupport
from ..http.types import HttpTransport, get_request, post_request
from ..idempotency.idempotency_key_generator import resolve_idempotency_key
from ..model.deposits import (
    CreatePaymentIntentResult,
    DepositResponse,
    PaymentIntentResponse,
    map_create_payment_intent_result,
    map_deposit_response,
    map_payment_intent_response,
)


class DepositsResource(ResourceSupport):
    """Data Plane -- Deposits (3 rotas reais)."""

    def __init__(self, transport: HttpTransport) -> None:
        super().__init__(transport)

    def create_payment_intent(
        self,
        organization_id: str,
        transaction_id: str,
        asset_network_id: str,
        amount: Decimal,
        expires_at: str | None = None,
        idempotency_key: str | None = None,
    ) -> CreatePaymentIntentResult:
        """deposit_address real so e exposto pelo GET dedicado (get_payment_intent) em seguida."""
        key = resolve_idempotency_key(idempotency_key)
        body = self._to_json({
            "transactionId": transaction_id, "assetNetworkId": asset_network_id, "amount": amount,
            "expiresAt": expires_at, "idempotencyKey": key,
        })
        return self._execute(post_request(f"/v1/organizations/{organization_id}/payment-intents", body, True), map_create_payment_intent_result)

    def get_payment_intent(self, payment_intent_id: str) -> PaymentIntentResponse:
        return self._execute(get_request(f"/v1/payment-intents/{payment_intent_id}"), map_payment_intent_response)

    def get_deposit(self, deposit_id: str) -> DepositResponse:
        return self._execute(get_request(f"/v1/deposits/{deposit_id}"), map_deposit_response)
