from __future__ import annotations

from decimal import Decimal
from typing import Iterator
from urllib.parse import urlencode

from .resource_support import ResourceSupport
from ..http.types import HttpTransport, get_request, post_request
from ..idempotency.idempotency_key_generator import resolve_idempotency_key
from ..model.data_plane import (
    CreateWithdrawalDestinationResult,
    WithdrawalQuoteResponse,
    WithdrawalResponse,
    map_create_withdrawal_destination_result,
    map_withdrawal_quote_response,
    map_withdrawal_response,
)
from ..model.enum_factory import EnumValue
from ..model.enums import WithdrawalStatus
from ..pagination.page_iterator import paginate
from ..util.polling import poll_until

_TERMINAL_STATUSES = {
    WithdrawalStatus.COMPLETED.raw_value,  # type: ignore[attr-defined]
    WithdrawalStatus.REJECTED.raw_value,  # type: ignore[attr-defined]
    WithdrawalStatus.CANCELLED.raw_value,  # type: ignore[attr-defined]
    WithdrawalStatus.BROADCAST_FAILED.raw_value,  # type: ignore[attr-defined]
}


class WithdrawalsResource(ResourceSupport):
    """
    Data Plane -- Withdrawals (7 real routes). quote() never writes anything (pure read); request()
    always exposes estimated_network_fee/estimated_recipient_amount in the response.
    """

    def __init__(self, transport: HttpTransport) -> None:
        super().__init__(transport)

    def quote(
        self, organization_id: str, account_id: str, withdrawal_destination_id: str, asset_network_id: str, amount: Decimal,
    ) -> WithdrawalQuoteResponse:
        body = self._to_json({
            "accountId": account_id, "withdrawalDestinationId": withdrawal_destination_id,
            "assetNetworkId": asset_network_id, "amount": amount,
        })
        return self._execute(post_request(f"/v1/organizations/{organization_id}/withdrawals/quote", body, True), map_withdrawal_quote_response)

    def create_destination(self, organization_id: str, address: str, asset_network_id: str) -> CreateWithdrawalDestinationResult:
        body = self._to_json({"address": address, "assetNetworkId": asset_network_id})
        return self._execute(post_request(f"/v1/organizations/{organization_id}/withdrawal-destinations", body, False), map_create_withdrawal_destination_result)

    def request(
        self,
        organization_id: str,
        account_id: str,
        withdrawal_destination_id: str,
        asset_network_id: str,
        amount: Decimal,
        idempotency_key: str | None = None,
    ) -> WithdrawalResponse:
        key = resolve_idempotency_key(idempotency_key)
        body = self._to_json({
            "accountId": account_id, "withdrawalDestinationId": withdrawal_destination_id,
            "assetNetworkId": asset_network_id, "amount": amount, "idempotencyKey": key,
        })
        return self._execute(post_request(f"/v1/organizations/{organization_id}/withdrawals", body, True), map_withdrawal_response)

    def get(self, withdrawal_id: str) -> WithdrawalResponse:
        return self._execute(get_request(f"/v1/withdrawals/{withdrawal_id}"), map_withdrawal_response)

    def list(
        self,
        organization_id: str,
        status: EnumValue[int] | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
        skip: int | None = None,
        take: int | None = None,
    ) -> list[WithdrawalResponse]:
        """
        skip/take are real pagination (one of only 2 endpoints in the SDK with true pagination).
        date_from/date_to go through urlencode -- never concatenated raw (same class of security
        finding fixed in webhook_endpoints_resource.py/all the other SDKs, see
        SECURITY_REVIEW.md).
        """
        params: dict[str, str] = {}
        if status is not None:
            params["status"] = str(status.raw_value)
        if date_from is not None:
            params["from"] = date_from
        if date_to is not None:
            params["to"] = date_to
        if skip is not None:
            params["skip"] = str(skip)
        if take is not None:
            params["take"] = str(take)
        suffix = f"?{urlencode(params)}" if params else ""
        return self._execute_list(get_request(f"/v1/organizations/{organization_id}/withdrawals{suffix}"), map_withdrawal_response)

    def list_all(
        self, organization_id: str, page_size: int, status: EnumValue[int] | None = None, date_from: str | None = None, date_to: str | None = None,
    ) -> Iterator[WithdrawalResponse]:
        """Lazy iterator -- see SDK_CAPABILITY_SPEC.md section 12.7."""
        return paginate(page_size, lambda skip, take: self.list(organization_id, status, date_from, date_to, skip, take))

    def cancel(self, withdrawal_id: str, reason: str | None = None) -> None:
        body = self._to_json({"reason": reason or ""})
        self._execute_no_content(post_request(f"/v1/withdrawals/{withdrawal_id}/cancel", body, False))

    def retry_broadcast(self, withdrawal_id: str) -> None:
        self._execute_no_content(post_request(f"/v1/withdrawals/{withdrawal_id}/retry-broadcast", None, False))

    def wait_for(self, withdrawal_id: str, timeout_seconds: float, poll_interval_seconds: float) -> WithdrawalResponse:
        """Safe polling, never infinite -- ends at Completed/Rejected/Cancelled/BroadcastFailed."""
        return poll_until(
            lambda: self.get(withdrawal_id),
            lambda r: r.status.raw_value in _TERMINAL_STATUSES,
            timeout_seconds,
            poll_interval_seconds,
            f"withdrawal_id={withdrawal_id}",
        )
