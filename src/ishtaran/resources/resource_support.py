"""
Common base for every resource -- request execution + lossless parsing + error mapping
centralized, so no resource duplicates this logic.
"""

from __future__ import annotations

import json
from decimal import Decimal
from typing import Any, Callable, TypeVar

from ..error.error_mapper import map_error
from ..http.types import HttpTransport, IshtaranHttpRequest
from ..model.enum_factory import EnumValue
from ..util.json_util import parse_lossless

T = TypeVar("T")


class ResourceSupport:
    def __init__(self, transport: HttpTransport) -> None:
        self._transport = transport

    def _execute(self, request: IshtaranHttpRequest, mapper: Callable[[Any], T]) -> T:
        response = self._transport.send(request)
        if response.status >= 400:
            raise map_error(response)
        if not response.body or not response.body.strip():
            return None  # type: ignore[return-value]
        return mapper(parse_lossless(response.body))

    def _execute_list(self, request: IshtaranHttpRequest, mapper: Callable[[Any], T]) -> list[T]:
        response = self._transport.send(request)
        if response.status >= 400:
            raise map_error(response)
        if not response.body or not response.body.strip():
            return []
        raw = parse_lossless(response.body)
        if not isinstance(raw, list):
            raise ValueError("Expected response as a list, received a different format")
        return [mapper(item) for item in raw]

    def _execute_optional(self, request: IshtaranHttpRequest, mapper: Callable[[Any], T]) -> T | None:
        """Like _execute, but a 204/empty body (a legitimate no-op, e.g. "no eligible candidates") maps to None instead of throwing."""
        response = self._transport.send(request)
        if response.status >= 400:
            raise map_error(response)
        if response.status == 204 or not response.body or not response.body.strip():
            return None
        return mapper(parse_lossless(response.body))

    def _execute_no_content(self, request: IshtaranHttpRequest) -> None:
        response = self._transport.send(request)
        if response.status >= 400:
            raise map_error(response)

    def _to_json(self, value: Any) -> str:
        """
        Minimal custom serializer -- necessary because standard json.dumps has no way to emit
        Decimal as a raw JSON number (it would always quote it as a string via `default=`, which
        the real API, expecting number/double, would reject). Never routes Decimal through float
        (would lose precision) -- emits the exact text via str(Decimal), unquoted, directly to the stream.
        """
        return _encode(value)


def _encode(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, (int, float)):
        return repr(value)
    if isinstance(value, str):
        return json.dumps(value)
    if isinstance(value, EnumValue):
        return _encode(value.raw_value)
    if isinstance(value, dict):
        items = ", ".join(f"{json.dumps(str(k))}: {_encode(v)}" for k, v in value.items())
        return "{" + items + "}"
    if isinstance(value, (list, tuple)):
        return "[" + ", ".join(_encode(item) for item in value) + "]"
    raise TypeError(f"Type not JSON-serializable: {type(value)}")
