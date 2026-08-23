"""
The real API sends money as number(double) in JSON (never a string -- see SDK_CAPABILITY_SPEC.md
section 11.1). Python's default parser (json.loads) converts numbers to float by default, which
would lose precision -- that's why all response parsing uses parse_float=Decimal AND parse_int=Decimal,
preserving the exact text of every number (integer or fractional) without ever going through float.
Genuinely small integer fields (decimals, confirmationCount, enum raw value) are converted
explicitly to int in the per-DTO mapping layer, never in the generic parsing layer.
"""

from __future__ import annotations

import json
from decimal import Decimal
from typing import Any, Callable, TypeVar

T = TypeVar("T")


def parse_lossless(text: str) -> Any:
    return json.loads(text, parse_float=Decimal, parse_int=Decimal)


def money(value: Any) -> Decimal:
    if value is None:
        raise ValueError("money: value missing where a monetary field was expected")
    return value if isinstance(value, Decimal) else Decimal(str(value))


def money_or_none(value: Any) -> Decimal | None:
    return None if value is None else money(value)


def safe_int(value: Any) -> int:
    if value is None:
        raise ValueError("safe_int: value missing")
    return int(value)


def safe_int_or_none(value: Any) -> int | None:
    return None if value is None else safe_int(value)


def field(raw: Any, name: str) -> Any:
    if not isinstance(raw, dict):
        raise ValueError(f'Expected an object to read field "{name}"')
    return raw.get(name)


def string_field(raw: Any, name: str) -> str:
    value = field(raw, name)
    if not isinstance(value, str):
        raise ValueError(f'Field "{name}" should be a string')
    return value


def string_field_or_none(raw: Any, name: str) -> str | None:
    value = field(raw, name)
    return None if value is None else str(value)


def bool_field(raw: Any, name: str) -> bool:
    value = field(raw, name)
    if not isinstance(value, bool):
        raise ValueError(f'Field "{name}" should be a bool')
    return value


def array_field(raw: Any, name: str, mapper: Callable[[Any], T]) -> list[T]:
    value = field(raw, name)
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError(f'Field "{name}" should be a list')
    return [mapper(item) for item in value]
