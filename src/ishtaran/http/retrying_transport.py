"""
Retry decorator -- see SDK_CAPABILITY_SPEC.md section 8. Only retries: connection/timeout failure
(always), HTTP 429 (always, honoring Retry-After when present), HTTP 5xx (only if
request.idempotent). Never retries 400/401/403/404/409/422 -- those are deterministic.
"""

from __future__ import annotations

import random
import time

from .types import HttpTransport, IshtaranHttpRequest, IshtaranHttpResponse
from ..config.retry_policy import RetryPolicy
from ..error.errors import NetworkError, TimeoutError


class RetryingTransport(HttpTransport):
    def __init__(self, delegate: HttpTransport, policy: RetryPolicy) -> None:
        self._delegate = delegate
        self._policy = policy

    def send(self, request: IshtaranHttpRequest) -> IshtaranHttpResponse:
        attempt = 0
        while True:
            try:
                response = self._delegate.send(request)
                if self._should_retry_status(response.status, request.idempotent) and attempt < self._policy.max_retries:
                    self._sleep_before_retry(attempt, response.header("Retry-After"))
                    attempt += 1
                    continue
                return response
            except (NetworkError, TimeoutError) as exc:
                if attempt < self._policy.max_retries:
                    self._sleep_before_retry(attempt, None)
                    attempt += 1
                    continue
                raise exc

    def _should_retry_status(self, status: int, idempotent: bool) -> bool:
        if status == 429:
            return True
        return 500 <= status < 600 and idempotent

    def _sleep_before_retry(self, attempt: int, retry_after_header: str | None) -> None:
        delay_ms = self._parse_retry_after_ms(retry_after_header) if retry_after_header else self._backoff_ms(attempt)
        time.sleep(delay_ms / 1000)

    def _backoff_ms(self, attempt: int) -> float:
        raw = self._policy.base_backoff_ms * (self._policy.backoff_multiplier ** attempt)
        capped = min(raw, self._policy.max_backoff_ms)
        jitter = random.uniform(0, max(1.0, capped / 4))
        return capped + jitter

    def _parse_retry_after_ms(self, header_value: str) -> float:
        try:
            return int(header_value.strip()) * 1000
        except ValueError:
            return self._backoff_ms(0)
