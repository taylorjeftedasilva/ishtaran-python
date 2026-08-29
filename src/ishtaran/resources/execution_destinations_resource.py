from __future__ import annotations

from .resource_support import ResourceSupport
from ..http.types import HttpTransport, post_request
from ..model.execution_custody import RegisterExecutionDestinationResult, map_register_execution_destination_result


class ExecutionDestinationsResource(ResourceSupport):
    """Data Plane -- ExecutionCustody ExecutionDestinations (DEC-037, CUSTODY-EXECUTION-MODES.md). Registers the on-chain address a beneficiary Account actually receives funds at, for a given AssetNetwork -- required before a Settlement involving that Account can execute under SelfCustody (the backend fails fast, before Signing/Broadcast, if none is registered)."""

    def __init__(self, transport: HttpTransport) -> None:
        super().__init__(transport)

    def register(self, organization_id: str, account_id: str, asset_network_id: str, address: str) -> RegisterExecutionDestinationResult:
        body = self._to_json({"accountId": account_id, "assetNetworkId": asset_network_id, "address": address})
        return self._execute(
            post_request(f"/v1/organizations/{organization_id}/execution-destinations", body, False),
            map_register_execution_destination_result,
        )
