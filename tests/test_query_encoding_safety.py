"""
Covers a real finding from this session: date_from/date_to (free-form strings) were concatenated
raw into the query string of WithdrawalsResource.list/LedgerResource.list_entries, the same risk
pattern already found and fixed in WebhookEndpointsResource. Fixed with urlencode in both.
"""

from decimal import Decimal

from ishtaran.resources.ledger_resource import LedgerResource
from ishtaran.resources.withdrawals_resource import WithdrawalsResource
from .fake_transport import FakeHttpTransport


def test_withdrawals_list_date_filter_is_url_encoded_never_injects_extra_params() -> None:
    fake = FakeHttpTransport().enqueue(FakeHttpTransport.json(200, "[]"))
    resource = WithdrawalsResource(fake)

    resource.list("org-1", date_from="2026-01-01&take=99999")

    path = fake.received[0].path
    assert "from=2026-01-01%26take%3D99999" in path


def test_ledger_list_entries_date_filter_is_url_encoded() -> None:
    fake = FakeHttpTransport().enqueue(FakeHttpTransport.json(200, "[]"))
    resource = LedgerResource(fake)

    resource.list_entries("acc-1", "an-1", skip=0, take=10, date_from="2026-01-01&skip=99999")

    path = fake.received[0].path
    assert "from=2026-01-01%26skip%3D99999" in path
