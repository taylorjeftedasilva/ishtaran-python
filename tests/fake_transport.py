"""In-memory transport, no network -- used by every resources/retry/error test."""

from __future__ import annotations

from collections import deque
from typing import Callable

from ishtaran.http.types import IshtaranHttpRequest, IshtaranHttpResponse


class FakeHttpTransport:
    def __init__(self) -> None:
        self._queued: deque[Callable[[IshtaranHttpRequest], IshtaranHttpResponse]] = deque()
        self._default: Callable[[IshtaranHttpRequest], IshtaranHttpResponse] | None = None
        self.received: list[IshtaranHttpRequest] = []

    def enqueue(self, response: IshtaranHttpResponse) -> "FakeHttpTransport":
        self._queued.append(lambda _req: response)
        return self

    def enqueue_raise(self, exc: Exception) -> "FakeHttpTransport":
        def _raise(_req: IshtaranHttpRequest) -> IshtaranHttpResponse:
            raise exc

        self._queued.append(_raise)
        return self

    def respond_always(self, responder: Callable[[IshtaranHttpRequest], IshtaranHttpResponse]) -> "FakeHttpTransport":
        self._default = responder
        return self

    def send(self, request: IshtaranHttpRequest) -> IshtaranHttpResponse:
        self.received.append(request)
        if self._queued:
            return self._queued.popleft()(request)
        if self._default:
            return self._default(request)
        raise RuntimeError("No response configured on FakeHttpTransport")

    @property
    def request_count(self) -> int:
        return len(self.received)

    @staticmethod
    def json(status: int, body: str, headers: dict[str, str] | None = None) -> IshtaranHttpResponse:
        return IshtaranHttpResponse(status=status, headers=headers or {}, body=body)
