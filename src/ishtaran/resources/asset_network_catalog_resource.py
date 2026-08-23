from __future__ import annotations

from .resource_support import ResourceSupport
from ..http.types import HttpTransport, get_request
from ..model.control_plane import (
    AssetNetworkResponse,
    AssetResponse,
    NetworkResponse,
    map_asset_network_response,
    map_asset_response,
    map_network_response,
)
from ..model.enum_factory import EnumValue

_STATUS_TO_RAW_INT = {"ENABLED": 1, "PAUSED": 2, "DISABLED": 3}


class AssetNetworkCatalogResource(ResourceSupport):
    """
    Catalog -- AssetNetworkCatalog (6 real routes, read-only within the SDK's scope). Always Member
    JWT -- does not accept an API Key today (real Known Gap, see SDK_CAPABILITY_SPEC.md section 12.3).
    """

    def __init__(self, transport: HttpTransport) -> None:
        super().__init__(transport)

    def list_assets(self) -> list[AssetResponse]:
        return self._execute_list(get_request("/v1/assets"), map_asset_response)

    def get_asset(self, asset_id: str) -> AssetResponse:
        return self._execute(get_request(f"/v1/assets/{asset_id}"), map_asset_response)

    def list_networks(self) -> list[NetworkResponse]:
        return self._execute_list(get_request("/v1/networks"), map_network_response)

    def get_network(self, network_id: str) -> NetworkResponse:
        return self._execute(get_request(f"/v1/networks/{network_id}"), map_network_response)

    def list_asset_networks(self, status: EnumValue[str] | None = None) -> list[AssetNetworkResponse]:
        """
        status is sent as a raw INTEGER in the query string, per the documented contract of the
        real OpenAPI -- even though the response returns status as a string (Group A).
        """
        path = "/v1/asset-networks"
        if status is not None:
            path += f"?status={self._to_request_raw_value(status)}"
        return self._execute_list(get_request(path), map_asset_network_response)

    def get_asset_network(self, asset_network_id: str) -> AssetNetworkResponse:
        return self._execute(get_request(f"/v1/asset-networks/{asset_network_id}"), map_asset_network_response)

    def _to_request_raw_value(self, status: EnumValue[str]) -> int:
        try:
            return _STATUS_TO_RAW_INT[status.name]
        except KeyError as exc:
            raise ValueError(f"Unknown AssetNetworkStatus value for filter: {status.name}") from exc
