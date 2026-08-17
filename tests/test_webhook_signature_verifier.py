import hashlib
import hmac
import time

from ishtaran.webhook.webhook_signature_verifier import compute_webhook_signature, verify_webhook_signature

SECRET = "whsec_test_secret_1234567890"


def test_accepts_correctly_computed_signature() -> None:
    body = '{"event":"payment.received","amount":100}'
    ts = int(time.time())
    signature = compute_webhook_signature(ts, body, SECRET)
    assert verify_webhook_signature(body, signature, str(ts), SECRET)


def test_rejects_tampered_payload() -> None:
    body = '{"event":"payment.received","amount":100}'
    ts = int(time.time())
    signature = compute_webhook_signature(ts, body, SECRET)
    tampered = '{"event":"payment.received","amount":999999}'
    assert not verify_webhook_signature(tampered, signature, str(ts), SECRET)


def test_rejects_tampered_signature() -> None:
    body = '{"event":"payment.received"}'
    ts = int(time.time())
    signature = compute_webhook_signature(ts, body, SECRET)
    tampered = signature[:-4] + "dead"
    assert not verify_webhook_signature(body, tampered, str(ts), SECRET)


def test_rejects_expired_timestamp() -> None:
    body = '{"event":"x"}'
    stale_ts = int(time.time()) - 2 * 60 * 60
    signature = compute_webhook_signature(stale_ts, body, SECRET)
    assert not verify_webhook_signature(body, signature, str(stale_ts), SECRET)


def test_rejects_wrong_secret() -> None:
    body = '{"event":"x"}'
    ts = int(time.time())
    signature = compute_webhook_signature(ts, body, SECRET)
    assert not verify_webhook_signature(body, signature, str(ts), "wrong-secret")


def test_accepts_uppercase_hex_signature() -> None:
    body = '{"event":"x"}'
    ts = int(time.time())
    signature = compute_webhook_signature(ts, body, SECRET).upper()
    assert verify_webhook_signature(body, signature, str(ts), SECRET)


def test_matches_known_vector_computed_independently_in_python_hmac() -> None:
    expected = hmac.new(b"topsecret", '1700000000.{"a":1}'.encode("utf-8"), hashlib.sha256).hexdigest()
    assert compute_webhook_signature(1700000000, '{"a":1}', "topsecret") == expected
    assert expected == "6a939b0c71853d606167625a15168ee9188c6a511c773ef4f42d307f3849e50f"
