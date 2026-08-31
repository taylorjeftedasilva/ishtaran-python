import json
from decimal import Decimal

from ishtaran.http.types import IshtaranHttpResponse
from ishtaran.resources.payout_resource import PayoutResource
from .fake_transport import FakeHttpTransport


def test_get_payable_summary_reads_accrued_reserved_for_payout_paid_never_available() -> None:
    body = json.dumps({"accrued": 40, "reservedForPayout": 0, "paid": 60})
    fake = FakeHttpTransport().enqueue(FakeHttpTransport.json(200, body))
    resource = PayoutResource(fake)

    summary = resource.get_payable_summary("acc-1", "an-1")

    assert summary.accrued == Decimal("40")
    assert summary.reserved_for_payout == Decimal("0")
    assert summary.paid == Decimal("60")
    assert fake.received[0].path == "/v1/accounts/acc-1/payable-summary?assetNetworkId=an-1"


def test_create_batch_auto_generates_an_idempotency_key_and_maps_the_created_id() -> None:
    body = json.dumps({"payoutBatchId": "pb-1"})
    fake = FakeHttpTransport().enqueue(FakeHttpTransport.json(201, body))
    resource = PayoutResource(fake)

    result = resource.create_batch("org-1", "env-1", "an-1", None)

    assert result.payout_batch_id == "pb-1"
    assert "idempotencyKey" in fake.received[0].body


def test_create_batch_maps_204_no_content_to_a_none_payout_batch_id_never_an_error() -> None:
    fake = FakeHttpTransport().enqueue(IshtaranHttpResponse(status=204, headers={}, body=""))
    resource = PayoutResource(fake)

    result = resource.create_batch("org-1", "env-1", "an-1", ["owner-1", "owner-2"])

    assert result.payout_batch_id is None


def test_get_batch_maps_the_full_obligation_tree_and_quote_snapshot() -> None:
    body = json.dumps({
        "payoutBatchId": "pb-1", "organizationId": "org-1", "environmentId": "env-1", "assetNetworkId": "an-1",
        "trigger": 2, "status": 3,
        "obligations": [{
            "ownerId": "owner-1", "amount": 100,
            "sourceObligations": [{"originReference": "settlement:s1", "amount": 100}],
            "destinationAddress": "Txxx", "status": 1,
        }],
        "networkExecutionQuoteSnapshot": {
            "network": "TRON", "nativeExecutionCost": 6.3, "resourceAssetNetworkId": "trx-an", "quoteCurrency": "USDT",
            "fx": 0.12, "totalCharged": 3.16456, "authorizedNativeCost": 6.3, "expiresAt": "2026-08-31T12:00:00Z",
        },
        "signingRequestId": "sr-1", "createdAt": "2026-08-31T11:00:00Z",
    })
    fake = FakeHttpTransport().enqueue(FakeHttpTransport.json(200, body))
    resource = PayoutResource(fake)

    batch = resource.get_batch("org-1", "pb-1")

    assert batch.trigger.name == "MANUAL"
    assert batch.status.name == "COMPLETED"
    assert batch.obligations[0].status.name == "CONFIRMED"
    assert batch.obligations[0].source_obligations[0].amount == Decimal("100")
    assert batch.network_execution_quote_snapshot.total_charged == Decimal("3.16456")
