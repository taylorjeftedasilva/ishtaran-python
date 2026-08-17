import uuid

from ishtaran.idempotency.idempotency_key_generator import generate_idempotency_key, resolve_idempotency_key


def test_never_overwrites_explicit_key() -> None:
    assert resolve_idempotency_key("my-explicit-key-123") == "my-explicit-key-123"


def test_generates_valid_uuid_v4_when_omitted_or_blank() -> None:
    generated = resolve_idempotency_key(None)
    assert uuid.UUID(generated).version == 4

    generated_from_blank = resolve_idempotency_key("  ")
    assert uuid.UUID(generated_from_blank).version == 4


def test_two_calls_never_produce_same_key() -> None:
    assert generate_idempotency_key() != generate_idempotency_key()
