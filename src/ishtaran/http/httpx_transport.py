"""
The only real implementation of HttpTransport -- built on httpx (the only production
dependency besides the stdlib's native lossless-json-equivalent -- see util/json_util.py). TLS
verified by default; never disabled by this SDK. Redirects are NEVER followed automatically
(parity with Java's Redirect.NEVER and with the security fix applied in the TypeScript SDK, see SECURITY_REVIEW.md).
"""

from __future__ import annotations

import httpx

from .types import HttpTransport, IshtaranHttpRequest, IshtaranHttpResponse
from ..config.client_config import IshtaranClientConfig
from ..error.errors import NetworkError, TimeoutError


class HttpxTransport(HttpTransport):
    def __init__(self, config: IshtaranClientConfig, transport: httpx.BaseTransport | None = None) -> None:
        """
        `transport` is a hook for testing only (injects httpx.MockTransport to exercise the real
        redirect policy without a network) -- production never passes this argument.
        """
        self._base_url = config.base_url
        self._user_agent = config.user_agent
        self._client = httpx.Client(
            timeout=httpx.Timeout(connect=config.connect_timeout_seconds, read=config.request_timeout_seconds,
                                   write=config.request_timeout_seconds, pool=config.request_timeout_seconds),
            follow_redirects=False,
            transport=transport,
        )

    def send(self, request: IshtaranHttpRequest) -> IshtaranHttpResponse:
        headers = {"User-Agent": self._user_agent, "Accept": "application/json", **request.headers}
        if request.body is not None:
            headers["Content-Type"] = "application/json"

        try:
            response = self._client.request(
                request.method, f"{self._base_url}{request.path}", headers=headers, content=request.body,
            )
        except httpx.TimeoutException as exc:
            raise TimeoutError(f"Timeout calling {request.method} {request.path}", exc) from exc
        except httpx.HTTPError as exc:
            raise NetworkError(f"Network failure calling {request.method} {request.path}", exc) from exc

        if 300 <= response.status_code < 400:
            raise NetworkError(
                f"Redirect ({response.status_code}) received calling {request.method} {request.path} -- "
                "this SDK never follows redirects automatically (same policy as the Java/TypeScript SDK)."
            )

        return IshtaranHttpResponse(status=response.status_code, headers=dict(response.headers), body=response.text)

    def close(self) -> None:
        self._client.close()
