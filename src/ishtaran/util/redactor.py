"""
Central secret masking for log/repr/error messages -- never the raw value. Generic format
(first 4 + **** + last 4): the real Ishtaran API Key has no environment prefix
(pure 32-byte Base64 -- see SDK_CAPABILITY_SPEC.md section 12.5), so this SDK never assumes a
sk_live_-style prefix that doesn't really exist.
"""

from __future__ import annotations

_SENSITIVE_HEADERS = {"authorization", "x-api-key"}


def mask(secret: str | None) -> str:
    if secret is None:
        return "None"
    if len(secret) <= 8:
        return "****"
    return f"{secret[:4]}****{secret[-4:]}"


def is_sensitive_header(header_name: str) -> bool:
    return header_name.lower() in _SENSITIVE_HEADERS
