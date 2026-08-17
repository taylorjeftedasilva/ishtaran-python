import pytest

from ishtaran.error.errors import NetworkError
from ishtaran.http.logging_transport import LoggingTransport
from ishtaran.http.types import get_request
from .fake_transport import FakeHttpTransport


def test_delegates_and_returns_real_response() -> None:
    fake = FakeHttpTransport().enqueue(FakeHttpTransport.json(200, '{"ok":true}'))
    logging_transport = LoggingTransport(fake)
    response = logging_transport.send(get_request("/x"))
    assert response.status == 200
    assert fake.request_count == 1


def test_exception_from_delegate_still_propagates() -> None:
    fake = FakeHttpTransport().enqueue_raise(NetworkError("boom"))
    logging_transport = LoggingTransport(fake)
    with pytest.raises(NetworkError):
        logging_transport.send(get_request("/x"))


def test_redacted_headers_never_exposes_api_key_or_authorization() -> None:
    logging_transport = LoggingTransport(FakeHttpTransport())
    request = get_request("/x")
    request = request.with_header("X-Api-Key", "supersecretapikeyvalue1234567890")
    request = request.with_header("Authorization", "Bearer supersecretjwttoken1234567890")
    request = request.with_header("User-Agent", "ishtaran-python/1.0.0")

    rendered = logging_transport.redacted_headers(request)

    assert "supersecretapikeyvalue1234567890" not in rendered
    assert "supersecretjwttoken1234567890" not in rendered
    assert "****" in rendered
    assert "ishtaran-python/1.0.0" in rendered
