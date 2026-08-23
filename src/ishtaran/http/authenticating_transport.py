"""
Attaches X-Api-Key (when configured) and/or Authorization: Bearer (when a Member login has
already happened on this client instance) -- never the two disguised as each other (rule from the brief).
"""

from __future__ import annotations

from .types import HttpTransport, IshtaranHttpRequest, IshtaranHttpResponse
from ..auth.bearer_token_holder import BearerTokenHolder

_API_KEY_HEADER = "X-Api-Key"


class AuthenticatingTransport(HttpTransport):
    def __init__(self, delegate: HttpTransport, api_key: str | None, bearer_token_holder: BearerTokenHolder) -> None:
        self._delegate = delegate
        self._api_key = api_key
        self._bearer_token_holder = bearer_token_holder

    def send(self, request: IshtaranHttpRequest) -> IshtaranHttpResponse:
        headers = dict(request.headers)
        if self._api_key:
            headers[_API_KEY_HEADER] = self._api_key
        token = self._bearer_token_holder.current()
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return self._delegate.send(IshtaranHttpRequest(request.method, request.path, headers, request.body, request.idempotent))
