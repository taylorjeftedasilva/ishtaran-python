"""
Gera a idempotency_key (campo de corpo, ou header em 2 endpoints especificos de
OrganizationTenancy -- ver SDK_CAPABILITY_SPEC.md secao 9) quando o consumidor nao fornece uma
explicitamente. UUID v4 -- mesmo formato aceito pelos campos Guid reais da API.
"""

from __future__ import annotations

import uuid


def generate_idempotency_key() -> str:
    return str(uuid.uuid4())


def resolve_idempotency_key(explicit_key: str | None) -> str:
    if explicit_key and explicit_key.strip():
        return explicit_key
    return generate_idempotency_key()
