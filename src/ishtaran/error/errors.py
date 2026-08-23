"""
Base of every exception raised by the SDK -- see SDK_CAPABILITY_SPEC.md section 6.4. http_status/code
are None for NetworkError/TimeoutError (no HTTP response ever existed); code/details are always None
for AuthenticationError/AuthorizationError (401/403 never have a body -- see section 6.3).
"""

from __future__ import annotations

from typing import Any


class IshtaranError(Exception):
    def __init__(
        self,
        message: str,
        *,
        http_status: int | None = None,
        code: str | None = None,
        request_id: str | None = None,
        details: Any = None,
        retryable: bool = False,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.http_status = http_status
        self.code = code
        # Always None today -- the real API does not implement any request/correlation ID
        # mechanism (exhaustive search in src/CompositionRoot/, zero occurrences -- see section 12.1).
        self.request_id = request_id
        self.details = details
        self.retryable = retryable


class AuthenticationError(IshtaranError):
    """401 -- no JSON body (see section 6.3). code/details are always None."""

    def __init__(self, message: str) -> None:
        super().__init__(message, http_status=401, retryable=False)


class AuthorizationError(IshtaranError):
    """403 -- no JSON body (see section 6.3)."""

    def __init__(self, message: str) -> None:
        super().__init__(message, http_status=403, retryable=False)


class ValidationError(IshtaranError):
    """400, code=VALIDATION_ERROR. message is ONE string with all errors joined by '; '."""

    def __init__(self, message: str, request_id: str | None, details: Any) -> None:
        super().__init__(message, http_status=400, code="VALIDATION_ERROR", request_id=request_id, details=details)


class NotFoundError(IshtaranError):
    """404, code=NOT_FOUND."""

    def __init__(self, message: str, request_id: str | None, details: Any) -> None:
        super().__init__(message, http_status=404, code="NOT_FOUND", request_id=request_id, details=details)


class ConflictError(IshtaranError):
    """409, any conflict code except IDEMPOTENCY_KEY_CONFLICT."""

    def __init__(self, message: str, code: str | None, request_id: str | None, details: Any) -> None:
        super().__init__(message, http_status=409, code=code, request_id=request_id, details=details)


class IdempotencyConflictError(ConflictError):
    """409, code=IDEMPOTENCY_KEY_CONFLICT -- same key resent with a different payload."""

    def __init__(self, message: str, request_id: str | None, details: Any) -> None:
        super().__init__(message, "IDEMPOTENCY_KEY_CONFLICT", request_id, details)


class RateLimitError(IshtaranError):
    """429, code=RATE_LIMITED. Always retryable -- exposes retry_after_seconds from the real header."""

    def __init__(self, message: str, request_id: str | None, details: Any, retry_after_seconds: int | None) -> None:
        super().__init__(message, http_status=429, code="RATE_LIMITED", request_id=request_id, details=details, retryable=True)
        self.retry_after_seconds = retry_after_seconds


class NetworkError(IshtaranError):
    """Transport failure -- no HTTP response at all. Always retryable."""

    def __init__(self, message: str, cause: BaseException | None = None) -> None:
        super().__init__(message, retryable=True)
        if cause is not None:
            self.__cause__ = cause


class TimeoutError(IshtaranError):  # noqa: A001 -- deliberately shadows builtins.TimeoutError,
    # to keep exact name parity with Java/TypeScript (brief rule) -- internal SDK code that needs
    # the real httpx network timeout uses httpx.TimeoutException, not the builtin, so there is no
    # practical collision within this package.
    """Connect/request timeout exceeded, or waitFor exceeding the deadline. Always retryable."""

    def __init__(self, message: str, cause: BaseException | None = None) -> None:
        super().__init__(message, retryable=True)
        if cause is not None:
            self.__cause__ = cause


class ApiError(IshtaranError):
    """Fallback -- any 4xx/5xx whose code is not recognized."""

    def __init__(self, message: str, http_status: int, code: str | None, request_id: str | None, details: Any, retryable: bool) -> None:
        super().__init__(message, http_status=http_status, code=code, request_id=request_id, details=details, retryable=retryable)
