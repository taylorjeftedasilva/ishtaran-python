from __future__ import annotations

from .resource_support import ResourceSupport
from ..http.types import HttpTransport, get_request, post_request
from ..idempotency.idempotency_key_generator import resolve_idempotency_key
from ..model.enum_factory import EnumValue
from ..model.execution_custody import (
    AllocatedDepositAddressResult,
    RegisterWalletResult,
    WalletPublicMaterialResult,
    WalletResponse,
    map_allocated_deposit_address_result,
    map_register_wallet_result,
    map_wallet_public_material_result,
    map_wallet_response,
)


class WalletsResource(ResourceSupport):
    """Data Plane -- ExecutionCustody Wallets (SPEC-018/021, checkpoint 10). The SDK only ever sends the extended PUBLIC key (public_derivation_material) -- generated locally by wallet.wallet_factory, never the private key/mnemonic (INV-SC-01)."""

    def __init__(self, transport: HttpTransport) -> None:
        super().__init__(transport)

    def register(
        self,
        application_id: str,
        network_id: str,
        scheme: EnumValue[int],
        public_derivation_material: str,
        idempotency_key: str | None = None,
    ) -> RegisterWalletResult:
        key = resolve_idempotency_key(idempotency_key)
        body = self._to_json({
            "networkId": network_id, "scheme": scheme.raw_value,
            "publicDerivationMaterial": public_derivation_material, "idempotencyKey": key,
        })
        return self._execute(post_request(f"/v1/applications/{application_id}/wallets", body, True), map_register_wallet_result)

    def register_for_account(
        self,
        organization_id: str,
        account_id: str,
        application_id: str,
        network_id: str,
        scheme: EnumValue[int],
        public_derivation_material: str,
        idempotency_key: str | None = None,
    ) -> RegisterWalletResult:
        """BR-TRF-008 -- registers the execution/signing identity OWNED by a specific Account (its
        own public_derivation_material, generated independently client-side -- never the same
        material as the Application's shared `register` Wallet). Required before that Account can
        be the source_account_id of a transfers.request(...) call for this network_id. Index 0 is
        reserved automatically as this Account's own receiving address (no separate
        allocate_deposit_address call needed for it)."""
        key = resolve_idempotency_key(idempotency_key)
        body = self._to_json({
            "applicationId": application_id, "networkId": network_id, "scheme": scheme.raw_value,
            "publicDerivationMaterial": public_derivation_material, "idempotencyKey": key,
        })
        return self._execute(
            post_request(f"/v1/organizations/{organization_id}/accounts/{account_id}/wallets", body, True),
            map_register_wallet_result,
        )

    def get(self, wallet_id: str) -> WalletResponse:
        """BR-WLT-002 -- never includes public_derivation_material; see get_public_material."""
        return self._execute(get_request(f"/v1/wallets/{wallet_id}"), map_wallet_response)

    def get_public_material(self, wallet_id: str) -> WalletPublicMaterialResult:
        return self._execute(get_request(f"/v1/wallets/{wallet_id}/public-material"), map_wallet_public_material_result)

    def allocate_deposit_address(self, application_id: str, network_id: str) -> AllocatedDepositAddressResult:
        """SPEC-018 BR-WLT-001 -- each call allocates a NEW index by design, with no idempotency_key; never reuse it on automatic retry."""
        body = self._to_json({"networkId": network_id})
        return self._execute(
            post_request(f"/v1/applications/{application_id}/wallets/deposit-addresses", body, False),
            map_allocated_deposit_address_result,
        )
