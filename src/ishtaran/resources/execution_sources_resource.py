from __future__ import annotations

from decimal import Decimal

from .resource_support import ResourceSupport
from ..http.types import HttpTransport, post_request
from ..model.execution_custody import RegisterExecutionSourceResult, map_register_execution_source_result


class ExecutionSourcesResource(ResourceSupport):
    """
    Data Plane -- ExecutionCustody ExecutionSources (CUSTODY-EXECUTION-MODES.md, SPEC-ADDRESSPOOL-001).
    Registers the address ExecutionCustody signs FROM to pay network cost for a given
    AssetNetwork -- required, together with a NetworkCostPayerAccountsResource, before the first
    self-custody Withdrawal/Payout on that AssetNetwork (the backend fails fast if none is
    registered).
    """

    def __init__(self, transport: HttpTransport) -> None:
        super().__init__(transport)

    def register(
        self,
        organization_id: str,
        environment_id: str,
        asset_network_id: str,
        wallet_id: str,
        derivation_reference: int,
        address: str | None,
    ) -> RegisterExecutionSourceResult:
        body = self._to_json({
            "environmentId": environment_id, "assetNetworkId": asset_network_id,
            "walletId": wallet_id, "derivationReference": derivation_reference, "address": address,
        })
        return self._execute(
            post_request(f"/v1/organizations/{organization_id}/execution-sources", body, False),
            map_register_execution_source_result,
        )

    def sync_resource_stake(
        self,
        organization_id: str,
        execution_source_id: str,
        available_native_amount: Decimal,
        available_energy: Decimal,
        available_bandwidth: Decimal,
    ) -> None:
        """
        F.18 -- self-reported (no on-chain verification in this version) declaration of the
        on-chain resource capacity available to the Wallet backing this ExecutionSource. Required
        before CUSTOMER_RESOURCES (SELF) mode can ever succeed for it -- the platform checks this
        declared stake for sufficiency at quote time. Safe to call again any time to re-sync (no
        first-registration-wins restriction, unlike register()).
        """
        body = self._to_json({
            "availableNativeAmount": available_native_amount,
            "availableEnergy": available_energy,
            "availableBandwidth": available_bandwidth,
        })
        self._execute_no_content(
            post_request(f"/v1/organizations/{organization_id}/execution-sources/{execution_source_id}/resource-stake", body, False),
        )
