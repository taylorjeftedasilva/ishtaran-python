from ishtaran.auth.bearer_token_holder import BearerTokenHolder
from ishtaran.http.authenticating_transport import AuthenticatingTransport
from ishtaran.http.types import get_request
from .fake_transport import FakeHttpTransport


def test_attaches_x_api_key_when_configured() -> None:
    fake = FakeHttpTransport().enqueue(FakeHttpTransport.json(200, "{}"))
    transport = AuthenticatingTransport(fake, "my-api-key", BearerTokenHolder())
    transport.send(get_request("/x"))
    assert fake.received[0].headers.get("X-Api-Key") == "my-api-key"


def test_bearer_token_set_after_construction_attached_to_subsequent_requests() -> None:
    fake = FakeHttpTransport().enqueue(FakeHttpTransport.json(200, "{}")).enqueue(FakeHttpTransport.json(200, "{}"))
    holder = BearerTokenHolder()
    transport = AuthenticatingTransport(fake, None, holder)

    transport.send(get_request("/before-login"))
    assert "Authorization" not in fake.received[0].headers

    holder.set("real-jwt-token")
    transport.send(get_request("/after-login"))
    assert fake.received[1].headers.get("Authorization") == "Bearer real-jwt-token"


def test_neither_header_attached_without_api_key_or_token() -> None:
    fake = FakeHttpTransport().enqueue(FakeHttpTransport.json(200, "{}"))
    transport = AuthenticatingTransport(fake, None, BearerTokenHolder())
    transport.send(get_request("/x"))
    assert "X-Api-Key" not in fake.received[0].headers
    assert "Authorization" not in fake.received[0].headers
