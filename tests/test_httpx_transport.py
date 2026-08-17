import httpx
import pytest

from ishtaran.config.client_config import build_client_config
from ishtaran.config.environment import Environment
from ishtaran.error.errors import NetworkError
from ishtaran.http.httpx_transport import HttpxTransport
from ishtaran.http.types import get_request


def test_never_follows_3xx_redirect_automatically_raises_network_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(302, headers={"Location": "https://evil.example.com/steal"})

    config = build_client_config(environment=Environment.LOCAL)
    transport = HttpxTransport(config, transport=httpx.MockTransport(handler))

    with pytest.raises(NetworkError):
        transport.send(get_request("/x"))


def test_passes_through_non_redirect_responses_normally() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text='{"ok":true}')

    config = build_client_config(environment=Environment.LOCAL)
    transport = HttpxTransport(config, transport=httpx.MockTransport(handler))

    response = transport.send(get_request("/x"))
    assert response.status == 200
    assert response.body == '{"ok":true}'
