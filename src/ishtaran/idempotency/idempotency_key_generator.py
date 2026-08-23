"""
Generates the idempotency_key (body field, or header on 2 specific OrganizationTenancy
endpoints -- see SDK_CAPABILITY_SPEC.md section 9) when the caller doesn't provide one
explicitly. UUID v4 -- same format accepted by the API's real Guid fields.
"""

from __future__ import annotations

import uuid


def generate_idempotency_key() -> str:
    return str(uuid.uuid4())


def resolve_idempotency_key(explicit_key: str | None) -> str:
    if explicit_key and explicit_key.strip():
        return explicit_key
    return generate_idempotency_key()
