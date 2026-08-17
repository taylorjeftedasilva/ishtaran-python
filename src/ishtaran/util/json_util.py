"""
A API real envia dinheiro como number(double) no JSON (nunca string -- ver SDK_CAPABILITY_SPEC.md
secao 11.1). O parser padrao do Python (json.loads) converte numeros para float por padrao, o que
perderia precisao -- por isso todo parsing de resposta usa parse_float=Decimal E parse_int=Decimal,
preservando o texto exato de todo numero (inteiro ou fracionario) sem nunca passar por float.
Campos genuinamente inteiros pequenos (decimals, confirmationCount, enum raw value) sao convertidos
explicitamente para int na camada de mapeamento por-DTO, nunca na camada de parsing generica.
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
        raise ValueError("money: valor ausente onde um campo monetario era esperado")
    return value if isinstance(value, Decimal) else Decimal(str(value))


def money_or_none(value: Any) -> Decimal | None:
    return None if value is None else money(value)


def safe_int(value: Any) -> int:
    if value is None:
        raise ValueError("safe_int: valor ausente")
    return int(value)


def safe_int_or_none(value: Any) -> int | None:
    return None if value is None else safe_int(value)


def field(raw: Any, name: str) -> Any:
    if not isinstance(raw, dict):
        raise ValueError(f'Esperado objeto para ler o campo "{name}"')
    return raw.get(name)


def string_field(raw: Any, name: str) -> str:
    value = field(raw, name)
    if not isinstance(value, str):
        raise ValueError(f'Campo "{name}" deveria ser string')
    return value


def string_field_or_none(raw: Any, name: str) -> str | None:
    value = field(raw, name)
    return None if value is None else str(value)


def bool_field(raw: Any, name: str) -> bool:
    value = field(raw, name)
    if not isinstance(value, bool):
        raise ValueError(f'Campo "{name}" deveria ser bool')
    return value


def array_field(raw: Any, name: str, mapper: Callable[[Any], T]) -> list[T]:
    value = field(raw, name)
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError(f'Campo "{name}" deveria ser lista')
    return [mapper(item) for item in value]
