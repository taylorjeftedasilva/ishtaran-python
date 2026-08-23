"""
Shared base for every wait_for in the SDK -- never infinite polling, always an explicit
timeout_seconds (see SDK_CAPABILITY_SPEC.md section 15).
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
            raise TimeoutError(f"wait_for exceeded the timeout of {timeout_seconds}s waiting for {description}")
        time.sleep(poll_interval_seconds)
