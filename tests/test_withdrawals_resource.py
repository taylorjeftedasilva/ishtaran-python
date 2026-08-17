from decimal import Decimal

from ishtaran.error.errors import NotFoundError, TimeoutError
from ishtaran.resources.withdrawals_resource import WithdrawalsResource
from .fake_transport import FakeHttpTransport
import pytest


def _withdrawal_json(withdrawal_id: str, status: int) -> str:
    return (
        '{"withdrawalId":"%s","organizationId":"org","accountId":"acc","withdrawalDestinationId":"dest",'
        '"assetNetworkId":"an","amount":100,"estimatedNetworkFee":0.4,"estimatedRecipientAmount":99.6,'
        '"finalNetworkFee":null,"finalRecipientAmount":null,"status":%d,"entryGroupId":null,'
        '"technicalReference":null,"createdAt":"2026-08-17T12:00:00Z"}' % (withdrawal_id, status)
    )


def test_quote_never_writes_anything_exposes_network_fee() -> None:
    body = (
        '{"accountId":"a1","withdrawalDestinationId":"d1","assetNetworkId":"an1",'
        '"requestedAmount":100,"estimatedNetworkFee":0.4,"estimatedRecipientAmount":99.6,'
        '"expiresAt":"2026-08-17T12:00:00Z"}'
    )
    fake = FakeHttpTransport().enqueue(FakeHttpTransport.json(200, body))
    resource = WithdrawalsResource(fake)

    quote = resource.quote("org-1", "a1", "d1", "an1", Decimal("100"))

    assert quote.estimated_network_fee == Decimal("0.4")
    assert quote.estimated_recipient_amount == Decimal("99.6")
    assert fake.request_count == 1
    assert fake.received[0].method == "POST"
    assert fake.received[0].path.endswith("/withdrawals/quote")


def test_request_auto_generates_idempotency_key_when_not_provided() -> None:
    fake = FakeHttpTransport().enqueue(FakeHttpTransport.json(201, _withdrawal_json("w1", 0)))
    resource = WithdrawalsResource(fake)

    result = resource.request("org-1", "a1", "d1", "an1", Decimal("100"))

    assert result.status.name == "REQUESTED"
    assert fake.received[0].body is not None
    assert "idempotencyKey" in fake.received[0].body


def test_get_not_found_maps_to_not_found_error() -> None:
    body = '{"status":404,"detail":"Withdrawal not found","code":"NOT_FOUND"}'
    fake = FakeHttpTransport().enqueue(FakeHttpTransport.json(404, body))
    resource = WithdrawalsResource(fake)

    with pytest.raises(NotFoundError):
        resource.get("missing")


def test_wait_for_polls_until_terminal_status() -> None:
    fake = FakeHttpTransport().enqueue(FakeHttpTransport.json(200, _withdrawal_json("w1", 2))).enqueue(FakeHttpTransport.json(200, _withdrawal_json("w1", 8)))
    resource = WithdrawalsResource(fake)

    result = resource.wait_for("w1", timeout_seconds=5, poll_interval_seconds=0.001)

    assert result.status.raw_value == 8
    assert fake.request_count == 2


def test_wait_for_never_resolving_raises_timeout_error() -> None:
    fake = FakeHttpTransport().respond_always(lambda _req: FakeHttpTransport.json(200, _withdrawal_json("w1", 2)))
    resource = WithdrawalsResource(fake)

    with pytest.raises(TimeoutError):
        resource.wait_for("w1", timeout_seconds=0.02, poll_interval_seconds=0.005)
