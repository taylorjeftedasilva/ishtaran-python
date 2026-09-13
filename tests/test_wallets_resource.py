import json

from ishtaran.model.enums import DerivationScheme
from ishtaran.resources.wallets_resource import WalletsResource
from .fake_transport import FakeHttpTransport


def test_register_for_account_posts_to_the_account_scoped_route_with_application_id_in_the_body() -> None:
    body = json.dumps({"walletId": "w1"})
    fake = FakeHttpTransport().enqueue(FakeHttpTransport.json(201, body))
    resource = WalletsResource(fake)

    result = resource.register_for_account(
        "org-1", "acc-1", "app-1", "net-1", DerivationScheme.TRON_BIP44_HARDENED_ACCOUNT, "xpub...", "idem-1",
    )

    assert result.wallet_id == "w1"
    assert fake.received[0].path == "/v1/organizations/org-1/accounts/acc-1/wallets"
    sent_body = json.loads(fake.received[0].body)
    assert sent_body["applicationId"] == "app-1"
    assert sent_body["networkId"] == "net-1"
    assert sent_body["publicDerivationMaterial"] == "xpub..."
    assert sent_body["idempotencyKey"] == "idem-1"


def test_register_for_account_auto_generates_idempotency_key_when_not_provided() -> None:
    body = json.dumps({"walletId": "w2"})
    fake = FakeHttpTransport().enqueue(FakeHttpTransport.json(201, body))
    resource = WalletsResource(fake)

    resource.register_for_account("org-1", "acc-1", "app-1", "net-1", DerivationScheme.TRON_BIP44_HARDENED_ACCOUNT, "xpub...")

    sent_body = json.loads(fake.received[0].body)
    assert isinstance(sent_body["idempotencyKey"], str)
    assert len(sent_body["idempotencyKey"]) > 0
