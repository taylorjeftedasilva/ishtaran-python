"""
Verificacao real de assinatura de webhook -- algoritmo extraido byte a byte de
WebhookSignatureCalculator.cs/HttpWebhookDeliveryPort.cs (ver SDK_CAPABILITY_SPEC.md secao 10):
signed_content = "{unix_timestamp}.{raw_body_json}",
signature = lowercase_hex(HMAC_SHA256(secret, signed_content)). Usa o raw_body exatamente como
recebido -- nunca reserializa o JSON antes de calcular.
"""

from __future__ import annotations

import hashlib
import hmac
import time

_DEFAULT_TOLERANCE_SECONDS = 5 * 60


def compute_webhook_signature(unix_timestamp_seconds: int, raw_body: str, endpoint_secret: str) -> str:
    signed_content = f"{unix_timestamp_seconds}.{raw_body}"
    return hmac.new(endpoint_secret.encode("utf-8"), signed_content.encode("utf-8"), hashlib.sha256).hexdigest()


def verify_webhook_signature(
    raw_body: str,
    signature_header: str,
    timestamp_header: str,
    endpoint_secret: str,
    tolerance_seconds: int = _DEFAULT_TOLERANCE_SECONDS,
) -> bool:
    if not raw_body or not signature_header or not timestamp_header or not endpoint_secret:
        return False

    try:
        timestamp_seconds = int(timestamp_header.strip())
    except ValueError:
        return False

    age_seconds = abs(time.time() - timestamp_seconds)
    if age_seconds > tolerance_seconds:
        return False

    expected = compute_webhook_signature(timestamp_seconds, raw_body, endpoint_secret)
    return hmac.compare_digest(expected, signature_header.strip().lower())
