from __future__ import annotations

from .resource_support import ResourceSupport
from ..http.types import HttpTransport, get_request, post_request
from ..idempotency.idempotency_key_generator import resolve_idempotency_key
from ..model.payout import (
    CreatePayoutBatchResult,
    PayableSummaryResponse,
    PayoutBatchResponse,
    map_payable_summary_response,
    map_payout_batch_response,
)
from ..util.json_util import string_field_or_none


class PayoutResource(ResourceSupport):
    """
    Data Plane -- Payout (SPEC-024/SPEC-025). Under PayoutPolicy.IMMEDIATE a beneficiary's
    Payable is settled the same moment as the Settlement itself (no PayoutBatch involved); under
    a batched policy the beneficiary only has an economic Receivable (get_payable_summary) until
    a PayoutBatch actually executes. This SDK slice only ever creates batches with
    trigger = MANUAL (the public route accepts no other trigger yet).
    """

    def __init__(self, transport: HttpTransport) -> None:
        super().__init__(transport)

    def get_payable_summary(self, account_id: str, asset_network_id: str) -> PayableSummaryResponse:
        return self._execute(
            get_request(f"/v1/accounts/{account_id}/payable-summary?assetNetworkId={asset_network_id}"),
            map_payable_summary_response,
        )

    def create_batch(
        self,
        organization_id: str,
        environment_id: str,
        asset_network_id: str,
        explicit_owner_ids: list[str] | None = None,
        idempotency_key: str | None = None,
    ) -> CreatePayoutBatchResult:
        """payout_batch_id is None when there were no eligible candidates (204 No Content, a legitimate no-op)."""
        key = resolve_idempotency_key(idempotency_key)
        body = self._to_json({
            "environmentId": environment_id, "assetNetworkId": asset_network_id,
            "explicitOwnerIds": explicit_owner_ids, "idempotencyKey": key,
        })
        payout_batch_id = self._execute_optional(
            post_request(f"/v1/organizations/{organization_id}/payout-batches", body, True),
            lambda raw: string_field_or_none(raw, "payoutBatchId"),
        )
        return CreatePayoutBatchResult(payout_batch_id=payout_batch_id)

    def get_batch(self, organization_id: str, payout_batch_id: str) -> PayoutBatchResponse:
        return self._execute(
            get_request(f"/v1/organizations/{organization_id}/payout-batches/{payout_batch_id}"),
            map_payout_batch_response,
        )
