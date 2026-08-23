from __future__ import annotations

from .resource_support import ResourceSupport
from ..http.types import HttpTransport, get_request, post_request
from ..idempotency.idempotency_key_generator import resolve_idempotency_key
from ..model.execution_custody import (
    CreateSigningRequestResult,
    ExecutionLegInput,
    SigningRequestResponse,
    SubmitSignedTransactionResult,
    map_create_signing_request_result,
    map_signing_request_response,
    map_submit_signed_transaction_result,
)


class SigningRequestsResource(ResourceSupport):
    """Data Plane -- ExecutionCustody SigningRequests (SPEC-019/020/021, checkpoint 10). The SDK never computes the canonical hash on create -- the backend computes it and returns it on get; the SDK only signs locally (wallet.signer) and submits it back."""

    def __init__(self, transport: HttpTransport) -> None:
        super().__init__(transport)

    def create(
        self,
        environment_id: str,
        wallet_id: str,
        derivation_reference: int,
        origin_reference: str,
        asset_network_id: str,
        source_address: str,
        legs: list[ExecutionLegInput],
        expires_at: str,
        idempotency_key: str | None = None,
    ) -> CreateSigningRequestResult:
        key = resolve_idempotency_key(idempotency_key)
        body = self._to_json({
            "walletId": wallet_id,
            "derivationReference": derivation_reference,
            "originReference": origin_reference,
            "assetNetworkId": asset_network_id,
            "sourceAddress": source_address,
            "legs": [{"role": leg.role, "destinationAddress": leg.destination_address, "amount": leg.amount} for leg in legs],
            "expiresAt": expires_at,
            "idempotencyKey": key,
        })
        return self._execute(
            post_request(f"/v1/environments/{environment_id}/signing-requests", body, True),
            map_create_signing_request_result,
        )

    def get(self, signing_request_id: str) -> SigningRequestResponse:
        return self._execute(get_request(f"/v1/signing-requests/{signing_request_id}"), map_signing_request_response)

    def submit_signed_transaction(
        self,
        signing_request_id: str,
        execution_leg_id: str,
        submitted_canonical_hash: str,
        signature_hex: str,
    ) -> SubmitSignedTransactionResult:
        """SPEC-020/INV-SC-03 -- submitted_canonical_hash must be exactly the canonical_hash returned by get for that Leg (compared byte for byte by the backend before verifying the signature, fail fast). signature_hex is the output of Signer.sign(...), uppercase hex."""
        body = self._to_json({"submittedCanonicalHash": submitted_canonical_hash, "signature": signature_hex})
        return self._execute(
            post_request(f"/v1/signing-requests/{signing_request_id}/legs/{execution_leg_id}/submit", body, False),
            map_submit_signed_transaction_result,
        )
