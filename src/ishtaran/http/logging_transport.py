"""
Logging opt-in (so ativo quando enable_logging=True na config) -- nunca loga
Authorization/X-Api-Key em texto puro (redacao central), nunca loga o corpo bruto.
"""

from __future__ import annotations

import logging
import time

from .types import HttpTransport, IshtaranHttpRequest, IshtaranHttpResponse
from ..util.redactor import is_sensitive_header, mask

_logger = logging.getLogger("ishtaran.http")


class LoggingTransport(HttpTransport):
    def __init__(self, delegate: HttpTransport) -> None:
        self._delegate = delegate

    def send(self, request: IshtaranHttpRequest) -> IshtaranHttpResponse:
        start = time.monotonic()
        _logger.debug("--> %s %s headers=%s", request.method, request.path, self.redacted_headers(request))
        try:
            response = self._delegate.send(request)
            elapsed_ms = round((time.monotonic() - start) * 1000)
            _logger.debug("<-- %s %s status=%s (%s ms)", request.method, request.path, response.status, elapsed_ms)
            return response
        except Exception as exc:
            elapsed_ms = round((time.monotonic() - start) * 1000)
            _logger.debug("<-- %s %s FAILED: %s (%s ms)", request.method, request.path, type(exc).__name__, elapsed_ms)
            raise

    def redacted_headers(self, request: IshtaranHttpRequest) -> str:
        parts = [f"{name}={mask(value) if is_sensitive_header(name) else value}" for name, value in request.headers.items()]
        return "{" + ", ".join(parts) + "}"
