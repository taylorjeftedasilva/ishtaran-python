from __future__ import annotations

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
