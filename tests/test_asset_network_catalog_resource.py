from ishtaran.model.enums import AssetNetworkStatus
from ishtaran.resources.asset_network_catalog_resource import AssetNetworkCatalogResource
from .fake_transport import FakeHttpTransport


def test_status_filter_sent_as_raw_integer() -> None:
    fake = FakeHttpTransport().enqueue(FakeHttpTransport.json(200, "[]"))
    resource = AssetNetworkCatalogResource(fake)

    resource.list_asset_networks(AssetNetworkStatus.PAUSED)  # type: ignore[attr-defined]

    assert "status=2" in fake.received[0].path


def test_no_filter_omits_status_param() -> None:
    fake = FakeHttpTransport().enqueue(FakeHttpTransport.json(200, "[]"))
    resource = AssetNetworkCatalogResource(fake)

    resource.list_asset_networks()

    assert "status=" not in fake.received[0].path
