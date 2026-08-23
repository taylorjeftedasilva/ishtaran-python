"""
Lazy generator over an endpoint with real skip/take pagination -- fetches the next page on
demand, never loads the entire collection at once (brief rule: "never unbounded bulk-loading").
Used only for the 2 endpoints in the SDK with truly real pagination (Withdrawals.list,
Ledger.list_entries -- see SDK_CAPABILITY_SPEC.md section 12.7); every other listing endpoint
returns a plain list (already iterable), without faking pagination the API doesn't have.
"""

from __future__ import annotations

from typing import Callable, Iterator, TypeVar

T = TypeVar("T")


def paginate(page_size: int, fetch_page: Callable[[int, int], list[T]]) -> Iterator[T]:
    if page_size <= 0:
        raise ValueError("page_size must be positive")
    skip = 0
    while True:
        page = fetch_page(skip, page_size)
        yield from page
        if len(page) < page_size:
            return
        skip += page_size
