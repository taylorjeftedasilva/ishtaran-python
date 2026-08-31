import json

from ishtaran.resources.execution_sources_resource import ExecutionSourcesResource
from .fake_transport import FakeHttpTransport


def test_register_posts_the_derivation_reference_and_address_maps_the_created_id() -> None:
    body = json.dumps({"executionSourceId": "es-1"})
    fake = FakeHttpTransport().enqueue(FakeHttpTransport.json(201, body))
    resource = ExecutionSourcesResource(fake)

    result = resource.register("org-1", "env-1", "an-1", "wallet-1", 42, "Txxx")

    assert result.execution_source_id == "es-1"
    assert fake.received[0].method == "POST"
    assert fake.received[0].path == "/v1/organizations/org-1/execution-sources"
    sent_body = json.loads(fake.received[0].body)
    assert sent_body == {"environmentId": "env-1", "assetNetworkId": "an-1", "walletId": "wallet-1", "derivationReference": 42, "address": "Txxx"}
