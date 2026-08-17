import json

from ishtaran.error.error_mapper import map_error
from ishtaran.error.errors import (
    ApiError,
    AuthenticationError,
    AuthorizationError,
    ConflictError,
    IdempotencyConflictError,
    NotFoundError,
    RateLimitError,
    ValidationError,
)
from ishtaran.http.types import IshtaranHttpResponse
from .fake_transport import FakeHttpTransport


def test_401_has_no_body_maps_to_authentication_error() -> None:
    error = map_error(IshtaranHttpResponse(status=401, headers={}, body=""))
    assert isinstance(error, AuthenticationError)
    assert error.code is None
    assert error.details is None


def test_403_has_no_body_maps_to_authorization_error() -> None:
    error = map_error(IshtaranHttpResponse(status=403, headers={}, body=""))
    assert isinstance(error, AuthorizationError)


def test_400_validation_error_is_single_string_never_a_structured_array() -> None:
    body = json.dumps({"status": 400, "detail": "Amount must be positive; AccountId is required", "code": "VALIDATION_ERROR"})
    error = map_error(FakeHttpTransport.json(400, body))
    assert isinstance(error, ValidationError)
    assert error.code == "VALIDATION_ERROR"
    assert "Amount must be positive; AccountId is required" in error.message


def test_404_maps_to_not_found_error() -> None:
    body = json.dumps({"status": 404, "detail": "Withdrawal not found", "code": "NOT_FOUND"})
    assert isinstance(map_error(FakeHttpTransport.json(404, body)), NotFoundError)


def test_409_idempotency_conflict_maps_to_idempotency_conflict_error_also_conflict_error() -> None:
    body = json.dumps({"status": 409, "detail": "reused", "code": "IDEMPOTENCY_KEY_CONFLICT"})
    error = map_error(FakeHttpTransport.json(409, body))
    assert isinstance(error, IdempotencyConflictError)
    assert isinstance(error, ConflictError)


def test_409_other_conflict_maps_to_plain_conflict_error_never_idempotency_subtype() -> None:
    body = json.dumps({"status": 409, "detail": "other conflict", "code": "SOME_OTHER_CONFLICT"})
    error = map_error(FakeHttpTransport.json(409, body))
    assert isinstance(error, ConflictError)
    assert not isinstance(error, IdempotencyConflictError)


def test_429_maps_to_rate_limit_error_with_retry_after_from_header() -> None:
    body = json.dumps({"status": 429, "code": "RATE_LIMITED"})
    response = FakeHttpTransport.json(429, body, {"Retry-After": "7"})
    error = map_error(response)
    assert isinstance(error, RateLimitError)
    assert error.retry_after_seconds == 7
    assert error.retryable is True


def test_5xx_unrecognized_code_falls_back_to_api_error() -> None:
    body = json.dumps({"status": 503, "detail": "Downstream dependency down", "code": "SOME_NEW_5XX_CODE"})
    error = map_error(FakeHttpTransport.json(503, body))
    assert isinstance(error, ApiError)
    assert error.http_status == 503
    assert error.code == "SOME_NEW_5XX_CODE"
    assert error.retryable is True


def test_malformed_body_never_raises_parsing_exception() -> None:
    error = map_error(FakeHttpTransport.json(500, "not json at all {{{"))
    assert isinstance(error, ApiError)
    assert error.http_status == 500
