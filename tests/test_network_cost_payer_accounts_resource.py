import json

import pytest

from ishtaran.error.errors import ConflictError
from ishtaran.model.enums import NetworkResourceSource
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


def test_update_resource_preference_patches_the_resource_preference_and_fallback_flag() -> None:
    fake = FakeHttpTransport().enqueue(FakeHttpTransport.json(204, ""))
    resource = NetworkCostPayerAccountsResource(fake)

    resource.update_resource_preference("org-1", "an-1", NetworkResourceSource.SELF, True)  # type: ignore[attr-defined]

    assert fake.received[0].method == "PATCH"
    assert fake.received[0].path == "/v1/organizations/org-1/network-cost-payer-accounts/an-1/resource-preference"
    sent_body = json.loads(fake.received[0].body)
    assert sent_body == {"resourcePreference": 1, "allowFallbackToIshtaranResources": True}
