"""
Covers a real finding from this session: the standard json.dumps has no way to emit a Decimal as
a raw JSON number (it would always quote it as a string via default=str, which the real API,
expecting number/double, would reject). ResourceSupport._to_json uses its own serializer to
avoid this.
"""

import json
from decimal import Decimal

from ishtaran.http.types import get_request
from ishtaran.model.enums import WithdrawalStatus
from ishtaran.resources.resource_support import ResourceSupport
from .fake_transport import FakeHttpTransport


class _DummyResource(ResourceSupport):
    def encode(self, value: object) -> str:
        return self._to_json(value)


def test_decimal_serializes_as_raw_json_number_never_quoted_string() -> None:
    resource = _DummyResource(FakeHttpTransport())
    encoded = resource.encode({"amount": Decimal("100.123456789012345678")})

    parsed = json.loads(encoded)
    assert isinstance(parsed["amount"], float) or "100.123456789012345678" in encoded
    # The real proof: the raw text contains the number unquoted, exactly as sent.
    assert '"amount": 100.123456789012345678' in encoded
    assert '"amount": "100.123456789012345678"' not in encoded


def test_enum_value_serializes_as_its_raw_value() -> None:
    resource = _DummyResource(FakeHttpTransport())
    status = WithdrawalStatus.from_raw(8)
    encoded = resource.encode({"status": status})
    assert '"status": 8' in encoded


def test_string_and_none_and_bool_still_encode_correctly() -> None:
    resource = _DummyResource(FakeHttpTransport())
    encoded = resource.encode({"name": "Acme \"Inc\"", "active": True, "deleted": None})
    parsed = json.loads(encoded)
    assert parsed == {"name": 'Acme "Inc"', "active": True, "deleted": None}


def test_nested_dict_and_list_encode_correctly() -> None:
    resource = _DummyResource(FakeHttpTransport())
    encoded = resource.encode({"participants": [{"accountId": "a1", "amount": Decimal("0.5")}]})
    assert '"amount": 0.5' in encoded
    assert '"accountId": "a1"' in encoded
