"""
Base compartilhada de todo wait_for do SDK -- nunca polling infinito, sempre timeout_seconds
explicito (ver SDK_CAPABILITY_SPEC.md secao 15).
"""

from __future__ import annotations

import time
from typing import Callable, TypeVar

from ..error.errors import TimeoutError

T = TypeVar("T")


def poll_until(
    fetch: Callable[[], T],
    is_done: Callable[[T], bool],
    timeout_seconds: float,
    poll_interval_seconds: float,
    description: str,
) -> T:
    deadline = time.monotonic() + timeout_seconds
    while True:
        result = fetch()
        if is_done(result):
            return result
        if time.monotonic() > deadline:
            raise TimeoutError(f"wait_for excedeu o timeout de {timeout_seconds}s aguardando {description}")
        time.sleep(poll_interval_seconds)
