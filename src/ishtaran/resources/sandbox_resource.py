from __future__ import annotations

from decimal import Decimal

from .resource_support import ResourceSupport
from ..http.types import HttpTransport, get_request, post_request
from ..model.enum_factory import EnumValue
from ..model.sandbox import (
    SandboxBroadcastAttemptResponse,
    SandboxBroadcastAttemptResult,
    SandboxObservedAddressResponse,
    SandboxObservedAddressResult,
    SandboxTreasuryObservedBalanceResponse,
    map_sandbox_broadcast_attempt_response,
    map_sandbox_broadcast_attempt_result,
    map_sandbox_observed_address_response,
    map_sandbox_observed_address_result,
    map_sandbox_treasury_observed_balance_response,
)


class SandboxResource(ResourceSupport):
    """
    Data Plane, exclusivo de Environment do tipo Sandbox -- Sandbox (9 rotas reais). Nunca
    disponivel/valido contra Production (o backend rejeita com 422 se o Environment nao for Sandbox).
    """

    def __init__(self, transport: HttpTransport) -> None:
        super().__init__(transport)

    def faucet(self, environment_id: str, deposit_address: str, asset_network_id: str, amount: Decimal) -> SandboxObservedAddressResult:
        body = self._to_json({"depositAddress": deposit_address, "assetNetworkId": asset_network_id, "amount": amount})
        return self._execute(post_request(f"/v1/environments/{environment_id}/sandbox/faucet", body, False), map_sandbox_observed_address_result)

    def simulate_deposit(self, environment_id: str, deposit_address: str, asset_network_id: str, amount: Decimal) -> SandboxObservedAddressResult:
        body = self._to_json({"depositAddress": deposit_address, "assetNetworkId": asset_network_id, "amount": amount})
        return self._execute(post_request(f"/v1/environments/{environment_id}/sandbox/simulate-deposit", body, False), map_sandbox_observed_address_result)

    def simulate_confirmation(self, environment_id: str, sandbox_observed_address_id: str, additional_confirmations: int, is_final: bool) -> None:
        body = self._to_json({"sandboxObservedAddressId": sandbox_observed_address_id, "additionalConfirmations": additional_confirmations, "isFinal": is_final})
        self._execute_no_content(post_request(f"/v1/environments/{environment_id}/sandbox/simulate-confirmation", body, False))

    def simulate_broadcast_confirmation(self, environment_id: str, broadcast_attempt_id: str, additional_confirmations: int, is_final: bool) -> None:
        body = self._to_json({"broadcastAttemptId": broadcast_attempt_id, "additionalConfirmations": additional_confirmations, "isFinal": is_final})
        self._execute_no_content(post_request(f"/v1/environments/{environment_id}/sandbox/simulate-broadcast-confirmation", body, False))

    def simulate_withdrawal(
        self, environment_id: str, destination_address: str, amount: Decimal, asset_network_id: str, outcome: EnumValue[int], failure_reason: str | None = None,
    ) -> SandboxBroadcastAttemptResult:
        body = self._to_json({
            "destinationAddress": destination_address, "amount": amount, "assetNetworkId": asset_network_id,
            "outcome": outcome.raw_value, "failureReason": failure_reason,
        })
        return self._execute(post_request(f"/v1/environments/{environment_id}/sandbox/simulate-withdrawal", body, False), map_sandbox_broadcast_attempt_result)

    def set_observed_treasury_balance(self, environment_id: str, asset_network_id: str, balance: Decimal) -> None:
        body = self._to_json({"assetNetworkId": asset_network_id, "balance": balance})
        self._execute_no_content(post_request(f"/v1/environments/{environment_id}/sandbox/treasury-balance", body, False))

    def get_treasury_balance(self, environment_id: str, asset_network_id: str) -> SandboxTreasuryObservedBalanceResponse:
        return self._execute(get_request(f"/v1/environments/{environment_id}/sandbox/treasury-balance/{asset_network_id}"), map_sandbox_treasury_observed_balance_response)

    def get_observed_address(self, environment_id: str, id_: str) -> SandboxObservedAddressResponse:
        return self._execute(get_request(f"/v1/environments/{environment_id}/sandbox/observed-addresses/{id_}"), map_sandbox_observed_address_response)

    def get_broadcast_attempt(self, environment_id: str, id_: str) -> SandboxBroadcastAttemptResponse:
        return self._execute(get_request(f"/v1/environments/{environment_id}/sandbox/broadcast-attempts/{id_}"), map_sandbox_broadcast_attempt_response)
