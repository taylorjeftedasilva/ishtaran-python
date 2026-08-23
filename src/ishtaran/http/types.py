"""
Internal request/response types, independent of any transport library -- never leaks httpx into
the public surface, allowing resources/* to be tested with a fake HttpTransport, no network.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol


@dataclass
class IshtaranHttpRequest:
    method: str
    path: str
    headers: dict[str, str] = field(default_factory=dict)
    body: str | None = None
    # Calls with an Idempotency-Key (or GET, naturally idempotent) can safely have 5xx retried
    # (section 8 of the Capability Spec).
    idempotent: bool = False

    def with_header(self, name: str, value: str | None) -> "IshtaranHttpRequest":
        if value is None:
            return self
        new_headers = {**self.headers, name: value}
        return IshtaranHttpRequest(self.method, self.path, new_headers, self.body, self.idempotent)


def get_request(path: str) -> IshtaranHttpRequest:
    return IshtaranHttpRequest(method="GET", path=path, idempotent=True)


def post_request(path: str, body: str | None, idempotent: bool) -> IshtaranHttpRequest:
    return IshtaranHttpRequest(method="POST", path=path, body=body, idempotent=idempotent)


def delete_request(path: str) -> IshtaranHttpRequest:
    return IshtaranHttpRequest(method="DELETE", path=path, idempotent=False)


@dataclass
class IshtaranHttpResponse:
    status: int
    headers: dict[str, str]
    body: str

    def header(self, name: str) -> str | None:
        lower = name.lower()
        for key, value in self.headers.items():
            if key.lower() == lower:
                return value
        return None


class HttpTransport(Protocol):
    """The only real implementation is HttpxTransport; tests use FakeHttpTransport, no network."""

    def send(self, request: IshtaranHttpRequest) -> IshtaranHttpResponse: ...
