from __future__ import annotations

from typing import Iterator
from urllib.parse import urlencode

from .resource_support import ResourceSupport
from ..http.types import HttpTransport, get_request
from ..model.data_plane import BalanceResponse, LedgerEntryResponse, map_balance_response, map_ledger_entry_response
from ..model.enum_factory import EnumValue
from ..pagination.page_iterator import paginate


class LedgerResource(ResourceSupport):
    """Data Plane -- Ledger (2 real routes, both read-only)."""

    def __init__(self, transport: HttpTransport) -> None:
        super().__init__(transport)

    def get_balance(self, account_id: str, asset_network_id: str) -> BalanceResponse:
        query = urlencode({"assetNetworkId": asset_network_id})
        return self._execute(get_request(f"/v1/accounts/{account_id}/balance?{query}"), map_balance_response)

    def list_entries(
        self,
        account_id: str,
        asset_network_id: str,
        skip: int,
        take: int,
        nature: EnumValue[int] | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> list[LedgerEntryResponse]:
        """
        skip/take are real pagination (see SDK_CAPABILITY_SPEC.md section 12.7). Every query value
        goes through urlencode -- never concatenated raw (see SECURITY_REVIEW.md).
        """
        params: dict[str, str] = {"assetNetworkId": asset_network_id, "skip": str(skip), "take": str(take)}
        if nature is not None:
            params["nature"] = str(nature.raw_value)
        if date_from is not None:
            params["from"] = date_from
        if date_to is not None:
            params["to"] = date_to
        return self._execute_list(get_request(f"/v1/accounts/{account_id}/ledger-entries?{urlencode(params)}"), map_ledger_entry_response)

    def list_all_entries(
        self,
        account_id: str,
        asset_network_id: str,
        page_size: int,
        nature: EnumValue[int] | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> Iterator[LedgerEntryResponse]:
        """Lazy iterator (generator) -- see SDK_CAPABILITY_SPEC.md section 12.7."""
        return paginate(page_size, lambda skip, take: self.list_entries(account_id, asset_network_id, skip, take, nature, date_from, date_to))
