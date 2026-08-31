import json

import pytest

from ishtaran.error.errors import ConflictError
from ishtaran.resources.network_cost_payer_accounts_resource import NetworkCostPayerAccountsResource
from .fake_transport import FakeHttpTransport


def test_register_posts_asset_network_id_and_account_id_maps_the_created_id() -> None:
    body = json.dumps({"networkCostPayerAccountId": "ncpa-1"})
    fake = FakeHttpTransport().enqueue(FakeHttpTransport.json(201, body))
    resource = NetworkCostPayerAccountsResource(fake)

    result = resource.register("org-1", "an-1", "acc-1")

    assert result.network_cost_payer_account_id == "ncpa-1"
    assert fake.received[0].path == "/v1/organizations/org-1/network-cost-payer-accounts"


def test_cross_tenant_account_is_rejected_mapped_to_a_4xx_error_never_a_raw_500() -> None:
    body = json.dumps({"status": 409, "detail": "Account does not belong to this Organization", "code": "CONFLICT"})
    fake = FakeHttpTransport().enqueue(FakeHttpTransport.json(409, body))
    resource = NetworkCostPayerAccountsResource(fake)

    with pytest.raises(ConflictError):
        resource.register("org-1", "an-1", "someone-elses-account")
