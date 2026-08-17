import json
import time
from decimal import Decimal

import pytest

from ishtaran.client import IshtaranClient
from ishtaran.error.errors import TimeoutError
from .fake_transport import FakeHttpTransport


def _transaction_json(transaction_id: str, status: int) -> str:
    return json.dumps({
        "transactionId": transaction_id, "organizationId": "org", "applicationId": "app",
        "workflowVersionId": None, "currentWorkflowStateId": None, "assetNetworkId": "an",
        "amount": 100, "status": status, "payerAccountId": "payer", "participants": [],
        "createdAt": "2026-08-17T12:00:00Z", "settledAmount": 0, "refundedAmount": 0,
    })


def _payment_intent_json(payment_intent_id: str, transaction_id: str, status: int, deposit_address: str) -> str:
    return json.dumps({
        "paymentIntentId": payment_intent_id, "organizationId": "org", "transactionId": transaction_id,
        "assetNetworkId": "an", "amount": 100, "status": status, "expiresAt": None,
        "depositAddress": deposit_address, "deposits": [], "createdAt": "2026-08-17T12:00:00Z",
    })


def test_receive_payment_composes_transaction_and_payment_intent() -> None:
    transaction_id, payment_intent_id = "t-1", "pi-1"
    fake = (
        FakeHttpTransport()
        .enqueue(FakeHttpTransport.json(201, json.dumps({"transactionId": transaction_id})))
        .enqueue(FakeHttpTransport.json(201, json.dumps({"paymentIntentId": payment_intent_id})))
        .enqueue(FakeHttpTransport.json(200, _transaction_json(transaction_id, 0)))
        .enqueue(FakeHttpTransport.json(200, _payment_intent_json(payment_intent_id, transaction_id, 0, "TDeposit1real")))
    )
    client = IshtaranClient.for_testing(fake)

    result = client.receive_payment("org", "app", "payer", "recipient", "an", Decimal("100"))

    assert result.transaction_id == transaction_id
    assert result.payment_intent_id == payment_intent_id
    assert result.deposit_address == "TDeposit1real"
    assert fake.request_count == 4


def test_wait_for_payment_polls_until_paid() -> None:
    transaction_id, payment_intent_id = "t-2", "pi-2"
    fake = (
        FakeHttpTransport()
        .enqueue(FakeHttpTransport.json(200, _transaction_json(transaction_id, 0)))
        .enqueue(FakeHttpTransport.json(200, _payment_intent_json(payment_intent_id, transaction_id, 0, "addr")))
        .enqueue(FakeHttpTransport.json(200, _transaction_json(transaction_id, 4)))
        .enqueue(FakeHttpTransport.json(200, _payment_intent_json(payment_intent_id, transaction_id, 2, "addr")))
    )
    client = IshtaranClient.for_testing(fake)

    result = client.wait_for_payment(transaction_id, payment_intent_id, timeout_seconds=5, poll_interval_seconds=0.001)

    assert result is not None
    assert fake.request_count == 4


def test_wait_for_payment_never_resolving_raises_timeout_error() -> None:
    transaction_id, payment_intent_id = "t-3", "pi-3"

    def responder(req):  # type: ignore[no-untyped-def]
        if "/transactions/" in req.path:
            return FakeHttpTransport.json(200, _transaction_json(transaction_id, 0))
        return FakeHttpTransport.json(200, _payment_intent_json(payment_intent_id, transaction_id, 0, "addr"))

    fake = FakeHttpTransport().respond_always(responder)
    client = IshtaranClient.for_testing(fake)

    with pytest.raises(TimeoutError):
        client.wait_for_payment(transaction_id, payment_intent_id, timeout_seconds=0.02, poll_interval_seconds=0.005)


def test_withdraw_composes_create_destination_and_request_never_hides_network_fee() -> None:

    destination_id = "d-1111"
    create_dest_body = json.dumps({"withdrawalDestinationId": destination_id})
    request_body = json.dumps({
        "withdrawalId": "w-1", "organizationId": "org", "accountId": "acc",
        "withdrawalDestinationId": destination_id, "assetNetworkId": "an", "amount": 50,
        "estimatedNetworkFee": 0.4, "estimatedRecipientAmount": 49.6, "finalNetworkFee": None,
        "finalRecipientAmount": None, "status": 0, "entryGroupId": None,
        "technicalReference": None, "createdAt": "2026-08-17T12:00:00Z",
    })
    fake = FakeHttpTransport().enqueue(FakeHttpTransport.json(201, create_dest_body)).enqueue(FakeHttpTransport.json(201, request_body))
    client = IshtaranClient.for_testing(fake)

    result = client.withdraw("org", "acc", "an", Decimal("50"), "TDestReal")

    assert result.withdrawal_id == "w-1"
    assert result.estimated_network_fee == Decimal("0.4")
    assert result.estimated_recipient_amount == Decimal("49.6")
    assert fake.request_count == 2


def test_get_balance_is_direct_pass_through() -> None:
    body = json.dumps({"available": 100, "pending": 0, "reserved": 0})
    fake = FakeHttpTransport().enqueue(FakeHttpTransport.json(200, body))
    client = IshtaranClient.for_testing(fake)

    balance = client.get_balance("acc", "an")
    assert balance.available == Decimal("100")


def test_verify_webhook_signature_makes_no_http_call() -> None:
    fake = FakeHttpTransport()  # nenhuma resposta enfileirada -- lancaria se fosse chamado
    client = IshtaranClient.for_testing(fake)

    valid = client.verify_webhook_signature("{}", "deadbeef", str(int(time.time())), "secret")
    assert valid is False
    assert fake.request_count == 0
