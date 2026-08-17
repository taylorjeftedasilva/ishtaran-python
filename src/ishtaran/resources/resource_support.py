"""
Base comum de todo resource -- execucao de request + parsing lossless + mapeamento de erro
centralizados, para nenhum resource duplicar essa logica.
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
            raise ValueError("Resposta esperada como lista, recebido outro formato")
        return [mapper(item) for item in raw]

    def _execute_no_content(self, request: IshtaranHttpRequest) -> None:
        response = self._transport.send(request)
        if response.status >= 400:
            raise map_error(response)

    def _to_json(self, value: Any) -> str:
        """
        Serializador proprio minimo -- necessario porque json.dumps padrao nao tem como emitir
        Decimal como numero JSON bruto (sempre o quotaria como string via `default=`, o que a API
        real, esperando number/double, rejeitaria). Nunca passa Decimal por float (perderia
        precisao) -- emite o texto exato via str(Decimal), sem aspas, diretamente no stream.
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
    raise TypeError(f"Tipo nao serializavel para JSON: {type(value)}")
