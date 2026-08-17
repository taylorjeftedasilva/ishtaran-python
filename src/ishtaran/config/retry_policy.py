"""
Politica de retry -- ver SDK_CAPABILITY_SPEC.md secao 8. Retry so em falha de conexao, 429
(respeitando Retry-After), e 5xx quando a chamada tem Idempotency-Key. Nunca em 4xx deterministico.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RetryPolicy:
    max_retries: int = 2
    base_backoff_ms: int = 200
    backoff_multiplier: float = 2.0
    max_backoff_ms: int = 5000


def default_retry_policy() -> RetryPolicy:
    return RetryPolicy()


def disabled_retry_policy() -> RetryPolicy:
    return RetryPolicy(max_retries=0, base_backoff_ms=0, backoff_multiplier=1.0, max_backoff_ms=0)
