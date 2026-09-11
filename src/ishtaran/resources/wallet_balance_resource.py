from __future__ import annotations

from urllib.parse import urlencode

from .resource_support import ResourceSupport
from ..http.types import HttpTransport, get_request, post_request
from ..model.wallet_balance import (
    WalletAssetBalanceResult,
    WalletBalanceResult,
    map_wallet_asset_balance_result,
    map_wallet_balance_result,
)


class WalletBalanceResource(ResourceSupport):
    """Ishtaran Wallet Balance / On-Chain Balance capability. The wallet's own on-chain balance --
    NEVER the Ledger (LedgerResource.get_balance, a fundamentally different question: "what does
    Ishtaran's own accounting say" vs "how many tokens actually sit at this address"). account_id
    is the wallet_id throughout -- ExecutionDestination already ties one Account to one registered
    self-custody address per AssetNetwork, so no separate wallet-registration concept exists (a
    distinct WalletsResource already exists for ExecutionCustody's own execution/signing wallets --
    an unrelated concept, deliberately not reused here to avoid confusing the two).

    get_balance is always cheap -- it never calls a blockchain/RPC provider, only returns the last
    known snapshot. Call refresh_balance to request a real, authoritative check; the platform
    enforces its own freshness window (currently 30s) and single-flight guard server-side, so
    calling it more often than needed is always safe (never causes extra provider cost, never an
    error) -- check refresh_suppressed/stale/next_refresh_allowed_at on the result rather than
    polling blindly."""

    def __init__(self, transport: HttpTransport) -> None:
        super().__init__(transport)

    def get_balance(self, account_id: str, environment_id: str, asset_network_id: str) -> WalletBalanceResult:
        query = urlencode({"environmentId": environment_id, "assetNetworkId": asset_network_id})
        return self._execute(get_request(f"/v1/accounts/{account_id}/wallet-balances?{query}"), map_wallet_balance_result)

    def refresh_balance(self, account_id: str, environment_id: str, asset_network_id: str) -> WalletBalanceResult:
        """Never informs what the new balance should be -- only asks the platform to check, authoritatively, itself."""
        query = urlencode({"environmentId": environment_id, "assetNetworkId": asset_network_id})
        return self._execute(
            post_request(f"/v1/accounts/{account_id}/wallet-balances/refresh?{query}", None, False), map_wallet_balance_result
        )

    def get_asset_balances(
        self, account_id: str, environment_id: str, asset_network_ids: list[str]
    ) -> list[WalletAssetBalanceResult]:
        """Aggregates balance across the given AssetNetworks, grouped by Asset (e.g. USDT total
        across TRON + Ethereum) -- asset_network_ids are candidates the caller already knows about
        (from asset_network_catalog.list_asset_networks, say); any candidate this Account has no
        registered address for is simply omitted from the result, never an error."""
        query = urlencode({"environmentId": environment_id, "assetNetworkIds": ",".join(asset_network_ids)})
        return self._execute_list(
            get_request(f"/v1/accounts/{account_id}/wallet-balances/aggregate?{query}"), map_wallet_asset_balance_result
        )
