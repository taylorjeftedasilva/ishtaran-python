import json
from decimal import Decimal

import pytest

from ishtaran.resources.transfers_resource import TransfersResource
from .fake_transport import FakeHttpTransport


def test_request_to_an_internal_account_auto_generates_idempotency_key_when_not_provided() -> None:
    # PROMPT 7.1/BR-TRF-008 (found live 2026-09-12) -- the creation endpoint itself only ever
    # acknowledges {"transferId": ...} (same convention as every other POST .../transfers-shaped
    # route in this platform) -- request() must follow up with a real GET to return a populated result.
    create_ack = json.dumps({"transferId": "t1"})
    full_body = json.dumps(
        {
            "transferId": "t1", "organizationId": "org-1", "applicationId": "app-1", "environmentId": "env-1",
            "sourceAccountId": "a1", "assetNetworkId": "an1", "amount": 100, "destinationAddress": "TRecipient...",
            "destinationAccountId": "a2", "platformFeeAmount": 0.2, "platformFeePercentage": 0.2,
            # request() ends in AwaitingSignature (real SigningRequest just created), never Confirmed
            # synchronously; the client still has to sign+submit each Leg.
            "status": 1, "signingRequestId": "sr-1",
            "createdAt": "2026-09-12T12:00:00Z", "confirmedAt": None, "failureReason": None,
        }
    )
    fake = FakeHttpTransport().enqueue(FakeHttpTransport.json(201, create_ack)).enqueue(FakeHttpTransport.json(200, full_body))
    resource = TransfersResource(fake)

    result = resource.request("org-1", "app-1", "env-1", "a1", "an1", Decimal("100"), destination_account_id="a2")

    assert result.status.name == "AWAITING_SIGNATURE"
    assert result.signing_request_id == "sr-1"
    # BR-TRF-004 -- amount is exactly what the recipient receives; the fee is separate.
    assert result.amount == Decimal("100")
    assert result.platform_fee_amount == Decimal("0.2")
    assert len(fake.received) == 2
    assert fake.received[0].method == "POST"
    assert fake.received[1].method == "GET"
    assert fake.received[1].path == "/v1/transfers/t1"
    sent_body = json.loads(fake.received[0].body)
    assert sent_body["destinationAccountId"] == "a2"
    assert sent_body["destinationAddress"] is None
    assert isinstance(sent_body["idempotencyKey"], str)
    assert len(sent_body["idempotencyKey"]) > 0


def test_request_to_an_external_address_never_requires_pre_registration() -> None:
    create_ack = json.dumps({"transferId": "t2"})
    full_body = json.dumps(
        {
            "transferId": "t2", "organizationId": "org-1", "applicationId": "app-1", "environmentId": "env-1",
            "sourceAccountId": "a1", "assetNetworkId": "an1", "amount": 50, "destinationAddress": "TExternalAddress...",
            "destinationAccountId": None, "platformFeeAmount": 0.1, "platformFeePercentage": 0.2,
            "status": 0, "signingRequestId": None, "createdAt": "2026-09-12T12:00:00Z", "confirmedAt": None, "failureReason": None,
        }
    )
    fake = FakeHttpTransport().enqueue(FakeHttpTransport.json(201, create_ack)).enqueue(FakeHttpTransport.json(200, full_body))
    resource = TransfersResource(fake)

    result = resource.request(
        "org-1", "app-1", "env-1", "a1", "an1", Decimal("50"),
        destination_address="TExternalAddress...", idempotency_key="my-key",
    )

    assert result.destination_account_id is None
    assert result.destination_address == "TExternalAddress..."
    sent_body = json.loads(fake.received[0].body)
    assert sent_body["destinationAddress"] == "TExternalAddress..."
    assert sent_body["destinationAccountId"] is None
    assert sent_body["idempotencyKey"] == "my-key"


def test_request_requires_exactly_one_of_destination_account_id_destination_address() -> None:
    resource = TransfersResource(FakeHttpTransport())

    with pytest.raises(ValueError):
        resource.request("org-1", "app-1", "env-1", "a1", "an1", Decimal("50"))

    with pytest.raises(ValueError):
        resource.request(
            "org-1", "app-1", "env-1", "a1", "an1", Decimal("50"),
            destination_account_id="a2", destination_address="TExternalAddress...",
        )


def test_get_maps_a_failed_transfer_exposing_failure_reason() -> None:
    body = json.dumps(
        {
            "transferId": "t3", "organizationId": "org-1", "applicationId": "app-1", "environmentId": "env-1",
            "sourceAccountId": "a1", "assetNetworkId": "an1", "amount": 100, "destinationAddress": "TX...",
            "destinationAccountId": None, "platformFeeAmount": 0.2, "platformFeePercentage": 0.2,
            "status": 4, "signingRequestId": "sr-3", "createdAt": "2026-09-12T12:00:00Z", "confirmedAt": None,
            "failureReason": "Insufficient balance",
        }
    )
    fake = FakeHttpTransport().enqueue(FakeHttpTransport.json(200, body))
    resource = TransfersResource(fake)

    result = resource.get("t3")

    assert result.status.name == "FAILED"
    assert result.failure_reason == "Insufficient balance"
