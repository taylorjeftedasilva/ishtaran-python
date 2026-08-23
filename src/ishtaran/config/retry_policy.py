"""
Retry policy -- see SDK_CAPABILITY_SPEC.md section 8. Retries only on connection failure, 429
(honoring Retry-After), and 5xx when the call carries an Idempotency-Key. Never on a deterministic 4xx.
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
