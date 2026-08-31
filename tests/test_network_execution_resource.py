import json
from decimal import Decimal

from ishtaran.model.enums import NetworkCostPayer, NetworkOperationKind
from ishtaran.model.execution_custody import NetworkExecutionOperationInput
from ishtaran.resources.network_execution_resource import NetworkExecutionResource
from .fake_transport import FakeHttpTransport


def test_quote_posts_operations_and_maps_the_full_structured_plan_inc18_scaling_proof() -> None:
    body = json.dumps({
        "network": "TRON",
        "plan": {
            "assetNetworkId": "an-1",
            "transactions": [
                {"transfers": [{"destinationAddress": "Txxx1", "amount": 40, "sourceOperationReference": "op-1"}]},
                {"transfers": [{"destinationAddress": "Txxx2", "amount": 60, "sourceOperationReference": "op-2"}]},
            ],
        },
        "estimatedResources": {"lines": [{"resourceCode": "ENERGY", "quantity": 15000, "unit": None}, {"resourceCode": "BANDWIDTH", "quantity": 350, "unit": None}]},
        "nativeExecutionCost": 6.3,
        "resourceAssetNetworkId": "trx-network-id",
        "quoteCurrency": "USDT",
        "fx": 0.12,
        "safetyBuffer": 0.05,
        "resourceSource": 1,
        "replenishmentRequirement": None,
        "conversionOverhead": 0.02,
        "expiresAt": "2026-08-31T12:00:00Z",
        "totalCharged": 3.16456,
        "networkCostPayer": 0,
        "authorizedNativeCost": 6.3,
    })
    fake = FakeHttpTransport().enqueue(FakeHttpTransport.json(200, body))
    resource = NetworkExecutionResource(fake)

    operations = [
        NetworkExecutionOperationInput(destination_address="Txxx1", amount=Decimal("40"), kind=NetworkOperationKind.TRANSFER, reference="op-1"),  # type: ignore[attr-defined]
        NetworkExecutionOperationInput(destination_address="Txxx2", amount=Decimal("60"), kind=NetworkOperationKind.TRANSFER, reference="op-2"),  # type: ignore[attr-defined]
    ]

    quote = resource.quote("env-1", "an-1", operations, NetworkCostPayer.INTEGRATOR)  # type: ignore[attr-defined]

    assert fake.received[0].method == "POST"
    assert fake.received[0].path == "/v1/environments/env-1/network-execution-quote"
    sent_body = json.loads(fake.received[0].body)
    assert len(sent_body["operations"]) == 2
    assert sent_body["operations"][0]["amount"] == 40
    assert sent_body["networkCostPayer"] == 0

    assert len(quote.plan.transactions) == 2
    assert quote.total_charged == Decimal("3.16456")
    assert quote.authorized_native_cost == Decimal("6.3")
    assert quote.resource_source.name == "SELF"
    assert quote.network_cost_payer.name == "INTEGRATOR"
    assert [line.resource_code for line in quote.estimated_resources.lines] == ["ENERGY", "BANDWIDTH"]


def test_quote_accepts_none_operations_a_size_only_estimate() -> None:
    body = json.dumps({
        "network": "TRON", "plan": {"assetNetworkId": "an-1", "transactions": []},
        "estimatedResources": {"lines": []}, "nativeExecutionCost": 0, "resourceAssetNetworkId": None,
        "quoteCurrency": None, "fx": 1, "safetyBuffer": 0, "resourceSource": 0, "replenishmentRequirement": None,
        "conversionOverhead": 0, "expiresAt": "2026-08-31T12:00:00Z", "totalCharged": 0, "networkCostPayer": 1,
        "authorizedNativeCost": 0,
    })
    fake = FakeHttpTransport().enqueue(FakeHttpTransport.json(200, body))
    resource = NetworkExecutionResource(fake)

    resource.quote("env-1", "an-1", None, NetworkCostPayer.REQUESTER)  # type: ignore[attr-defined]

    sent_body = json.loads(fake.received[0].body)
    assert sent_body["operations"] is None
