from __future__ import annotations

from .resource_support import ResourceSupport
from ..http.types import HttpTransport, post_request
from ..model.execution_custody import RegisterNetworkCostPayerAccountResult, map_register_network_cost_payer_account_result


class NetworkCostPayerAccountsResource(ResourceSupport):
    """
    Data Plane -- ExecutionCustody NetworkCostPayerAccounts (SPEC-NETEXEC-001). Registers the
    Account debited for the *charged* network cost of a NetworkExecutionQuote (total_charged, in
    quote_currency). account_id must belong to the caller's own Organization -- a cross-tenant
    Account is rejected. First-registration-wins per (organization_id, asset_network_id).
    """

    def __init__(self, transport: HttpTransport) -> None:
        super().__init__(transport)

    def register(self, organization_id: str, asset_network_id: str, account_id: str) -> RegisterNetworkCostPayerAccountResult:
        body = self._to_json({"assetNetworkId": asset_network_id, "accountId": account_id})
        return self._execute(
            post_request(f"/v1/organizations/{organization_id}/network-cost-payer-accounts", body, False),
            map_register_network_cost_payer_account_result,
        )
