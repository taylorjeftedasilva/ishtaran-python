from __future__ import annotations

from .resource_support import ResourceSupport
from ..http.types import HttpTransport, post_request
from ..model.enum_factory import EnumValue
from ..model.execution_custody import (
    NetworkExecutionOperationInput,
    NetworkExecutionQuoteResponse,
    map_network_execution_quote_response,
)


class NetworkExecutionResource(ResourceSupport):
    """
    Data Plane -- ExecutionCustody Network Execution Engine (SPEC-NETEXEC-001). A quote is a
    priced, time-boxed plan for 1..N physical on-chain operations; it never writes anything by
    itself (Settlement/Withdrawal/Payout each get/re-get their own quote internally at execution
    time -- preview quote != execution quote, never reuse this response as a price guarantee).
    """

    def __init__(self, transport: HttpTransport) -> None:
        super().__init__(transport)

    def quote(
        self,
        environment_id: str,
        asset_network_id: str,
        operations: list[NetworkExecutionOperationInput] | None,
        network_cost_payer: EnumValue[int],
    ) -> NetworkExecutionQuoteResponse:
        body = self._to_json({
            "assetNetworkId": asset_network_id,
            "operations": None if operations is None else [
                {
                    "destinationAddress": op.destination_address,
                    "amount": op.amount,
                    "kind": op.kind,
                    "reference": op.reference,
                }
                for op in operations
            ],
            "networkCostPayer": network_cost_payer,
        })
        return self._execute(
            post_request(f"/v1/environments/{environment_id}/network-execution-quote", body, True),
            map_network_execution_quote_response,
        )
