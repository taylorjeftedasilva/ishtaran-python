from __future__ import annotations

from decimal import Decimal

from .resource_support import ResourceSupport
from ..http.types import HttpTransport, get_request, post_request
from ..idempotency.idempotency_key_generator import resolve_idempotency_key
from ..model.transfer import TransferResponse, map_transfer_response


class TransfersResource(ResourceSupport):
    """Data Plane -- first-class Transfer (SPEC-TRANSFER-001) -- Account/Wallet -> asset -> another
    internal Account or an arbitrary external address, never a Payment/PaymentIntent/Settlement in
    disguise. Exactly one of destination_account_id/destination_address must be given -- an
    external destination never needs to be pre-registered (unlike withdrawals.create_destination).
    Platform Fee (platform_fee_amount on the response) is always ON_TOP -- amount is exactly what
    the recipient receives, the fee is charged separately from the sender."""

    def __init__(self, transport: HttpTransport) -> None:
        super().__init__(transport)

    def request(
        self,
        organization_id: str,
        application_id: str,
        environment_id: str,
        source_account_id: str,
        asset_network_id: str,
        amount: Decimal,
        destination_account_id: str | None = None,
        destination_address: str | None = None,
        idempotency_key: str | None = None,
    ) -> TransferResponse:
        """The creation endpoint itself only ever acknowledges {"transferId": ...} (same convention
        as every other POST .../transfers-shaped route in this platform, e.g. Settlement/
        Withdrawal) -- never the full record. This method does the create, then immediately follows
        up with get() so the caller receives a genuinely populated TransferResponse (status,
        signing_request_id, platform_fee_amount, ...) in one call. Found live (2026-09-12): an
        earlier version mapped the bare create ack itself through map_transfer_response, which
        raised ValueError on the first missing field instead of ever returning a usable result."""
        if (destination_account_id is None) == (destination_address is None):
            raise ValueError("Exactly one of destination_account_id/destination_address must be given.")

        key = resolve_idempotency_key(idempotency_key)
        body = self._to_json({
            "applicationId": application_id,
            "environmentId": environment_id,
            "sourceAccountId": source_account_id,
            "assetNetworkId": asset_network_id,
            "amount": amount,
            "destinationAccountId": destination_account_id,
            "destinationAddress": destination_address,
            "idempotencyKey": key,
        })
        created = self._execute(post_request(f"/v1/organizations/{organization_id}/transfers", body, True), lambda raw: raw)
        return self.get(created["transferId"])

    def get(self, transfer_id: str) -> TransferResponse:
        return self._execute(get_request(f"/v1/transfers/{transfer_id}"), map_transfer_response)
