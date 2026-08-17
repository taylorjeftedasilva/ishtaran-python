from ishtaran.config.retry_policy import RetryPolicy, disabled_retry_policy
from ishtaran.error.errors import NetworkError
from ishtaran.http.retrying_transport import RetryingTransport
from ishtaran.http.types import get_request, post_request
from .fake_transport import FakeHttpTransport

FAST_POLICY = RetryPolicy(max_retries=2, base_backoff_ms=1, backoff_multiplier=1.0, max_backoff_ms=5)


def test_never_retries_400() -> None:
    fake = FakeHttpTransport().enqueue(FakeHttpTransport.json(400, "{}"))
    retrying = RetryingTransport(fake, FAST_POLICY)
    retrying.send(post_request("/x", "{}", True))
    assert fake.request_count == 1


def test_429_retried_up_to_max_retries_then_returns_last_response() -> None:
    fake = FakeHttpTransport().enqueue(FakeHttpTransport.json(429, "{}")).enqueue(FakeHttpTransport.json(429, "{}")).enqueue(FakeHttpTransport.json(429, "{}"))
    retrying = RetryingTransport(fake, FAST_POLICY)
    response = retrying.send(post_request("/x", "{}", True))
    assert response.status == 429
    assert fake.request_count == 3


def test_503_on_idempotent_request_is_retried() -> None:
    fake = FakeHttpTransport().enqueue(FakeHttpTransport.json(503, "{}")).enqueue(FakeHttpTransport.json(200, '{"ok":true}'))
    retrying = RetryingTransport(fake, FAST_POLICY)
    response = retrying.send(get_request("/x"))
    assert response.status == 200
    assert fake.request_count == 2


def test_503_on_non_idempotent_request_never_retried() -> None:
    fake = FakeHttpTransport().enqueue(FakeHttpTransport.json(503, "{}"))
    retrying = RetryingTransport(fake, FAST_POLICY)
    response = retrying.send(post_request("/x", "{}", False))
    assert response.status == 503
    assert fake.request_count == 1


def test_connection_failure_retried_then_raises() -> None:
    fake = (
        FakeHttpTransport()
        .enqueue_raise(NetworkError("conn reset"))
        .enqueue_raise(NetworkError("conn reset"))
        .enqueue_raise(NetworkError("conn reset"))
    )
    retrying = RetryingTransport(fake, FAST_POLICY)
    try:
        retrying.send(get_request("/x"))
        assert False, "deveria ter lancado NetworkError"
    except NetworkError:
        pass
    assert fake.request_count == 3


def test_retry_disabled_never_retries() -> None:
    fake = FakeHttpTransport().enqueue(FakeHttpTransport.json(429, "{}"))
    retrying = RetryingTransport(fake, disabled_retry_policy())
    retrying.send(get_request("/x"))
    assert fake.request_count == 1
