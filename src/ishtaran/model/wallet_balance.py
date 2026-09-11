from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from ..util.json_util import bool_field, field, money, string_field, string_field_or_none


@dataclass(frozen=True)
class WalletBalanceResult:
    """Ishtaran Wallet Balance / On-Chain Balance capability -- the wallet's own on-chain balance,
    NEVER the Ledger (client.ledger.get_balance). account_id is the wallet_id throughout:
    ExecutionDestination (the registered self-custody address) already ties one Account to one
    (account_id, asset_network_id) -> address, so no separate wallet-registration concept exists."""

    account_id: str
    asset_network_id: str
    address: str
    balance: Decimal
    observed_at: str | None
    """None if this wallet has never been successfully observed yet -- balance is 0 in that case, never a lie."""
    block_reference: str | None
    source: str | None
    """"sandbox" | "trongrid" | etc -- whichever provider actually answered, reported honestly by the adapter itself."""
    stale: bool
    """True if observed_at is None or older than the platform's freshness window (currently 30s)."""
    next_refresh_allowed_at: str | None
    refresh_suppressed: bool
    """True if a refresh_balance call was suppressed by the freshness window or single-flight guard -- never an error."""
    refresh_failure_reason: str | None
    """Set only when the most recent refresh attempt failed -- balance/observed_at above remain the last successfully observed values, never zeroed out."""


def map_wallet_balance_result(raw: Any) -> WalletBalanceResult:
    return WalletBalanceResult(
        account_id=string_field(raw, "accountId"),
        asset_network_id=string_field(raw, "assetNetworkId"),
        address=string_field(raw, "address"),
        balance=money(field(raw, "balance")),
        observed_at=string_field_or_none(raw, "observedAt"),
        block_reference=string_field_or_none(raw, "blockReference"),
        source=string_field_or_none(raw, "source"),
        stale=bool_field(raw, "stale"),
        next_refresh_allowed_at=string_field_or_none(raw, "nextRefreshAllowedAt"),
        refresh_suppressed=bool_field(raw, "refreshSuppressed"),
        refresh_failure_reason=string_field_or_none(raw, "refreshFailureReason"),
    )


@dataclass(frozen=True)
class WalletNetworkBalanceResult:
    asset_network_id: str
    network_code: str
    balance: Decimal
    observed_at: str | None
    stale: bool


def _map_wallet_network_balance_result(raw: Any) -> WalletNetworkBalanceResult:
    return WalletNetworkBalanceResult(
        asset_network_id=string_field(raw, "assetNetworkId"),
        network_code=string_field(raw, "networkCode"),
        balance=money(field(raw, "balance")),
        observed_at=string_field_or_none(raw, "observedAt"),
        stale=bool_field(raw, "stale"),
    )


@dataclass(frozen=True)
class WalletAssetBalanceResult:
    """A single Asset's balance aggregated across the AssetNetworks the caller asked about --
    never summed across different Assets (e.g. USDT never added to ETH)."""

    asset_id: str
    asset_symbol: str
    aggregate_balance: Decimal
    network_balances: list[WalletNetworkBalanceResult]


def map_wallet_asset_balance_result(raw: Any) -> WalletAssetBalanceResult:
    network_balances_raw = field(raw, "networkBalances") or []
    return WalletAssetBalanceResult(
        asset_id=string_field(raw, "assetId"),
        asset_symbol=string_field(raw, "assetSymbol"),
        aggregate_balance=money(field(raw, "aggregateBalance")),
        network_balances=[_map_wallet_network_balance_result(item) for item in network_balances_raw],
    )
