"""
Translates a real error IshtaranHttpResponse into the correct IshtaranError subtype -- see
SDK_CAPABILITY_SPEC.md section 6. 401/403 never have a body (section 6.3); the other 4xx/5xx
usually carry ProblemDetails, but the mapper never raises if the body comes back empty/malformed.
"""

from __future__ import annotations

import json
from typing import Any

from ..http.types import IshtaranHttpResponse
from .errors import (
    ApiError,
    AuthenticationError,
    AuthorizationError,
    ConflictError,
    IdempotencyConflictError,
    IshtaranError,
    NotFoundError,
    RateLimitError,
    ValidationError,
)


def map_error(response: IshtaranHttpResponse) -> IshtaranError:
    status = response.status
    request_id = response.header("X-Request-Id") or response.header("X-Correlation-Id")

    if status == 401:
        return AuthenticationError("Authentication failed (401) -- missing/invalid API Key or token.")
    if status == 403:
        return AuthorizationError("Unauthorized (403) -- valid credential, but no permission for this operation.")

    problem = _try_parse(response.body)
    code = problem.get("code") if problem else None
    detail = (problem.get("detail") if problem else None) or f"HTTP Error {status}"

    if status == 429:
        retry_after_header = response.header("Retry-After")
        retry_after_seconds = int(retry_after_header) if retry_after_header and retry_after_header.isdigit() else None
        return RateLimitError(detail, request_id, problem, retry_after_seconds)
    if status == 400 and code == "VALIDATION_ERROR":
        return ValidationError(detail, request_id, problem)
    if status == 404:
        return NotFoundError(detail, request_id, problem)
    if status == 409 and code == "IDEMPOTENCY_KEY_CONFLICT":
        return IdempotencyConflictError(detail, request_id, problem)
    if status == 409:
        return ConflictError(detail, code, request_id, problem)

    retryable = status >= 500
    return ApiError(detail, status, code, request_id, problem, retryable)


def _try_parse(body: str) -> dict[str, Any] | None:
    if not body or not body.strip():
        return None
    try:
        parsed = json.loads(body)
        return parsed if isinstance(parsed, dict) else None
    except (json.JSONDecodeError, ValueError):
        return None
