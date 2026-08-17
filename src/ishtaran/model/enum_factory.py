"""
Fabrica generica de enum forward-compatible -- ver SDK_CAPABILITY_SPEC.md secao 11.4. Um valor
bruto desconhecido nunca lanca: vira EnumValue(name='UNKNOWN', raw_value=raw) preservando o valor
exato recebido (inteiro ou string, conforme o Grupo do enum real -- ver secao 11.3).

Deliberadamente NAO usa enum.Enum/IntEnum da stdlib: ambos lancam ValueError para um valor
desconhecido por padrao, o oposto do comportamento forward-compatible exigido pelo brief.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, TypeVar

TRaw = TypeVar("TRaw", int, str)


@dataclass(frozen=True)
class EnumValue(Generic[TRaw]):
    name: str
    raw_value: TRaw

    def __eq__(self, other: object) -> bool:
        return isinstance(other, EnumValue) and self.raw_value == other.raw_value

    def __hash__(self) -> int:
        return hash(self.raw_value)

    def __repr__(self) -> str:
        return f"{self.name}({self.raw_value!r})"


class EnumRegistry(Generic[TRaw]):
    """Instancia retornada por create_enum -- acesso por atributo (STATUS.COMPLETED) + from_raw()."""

    def __init__(self, members: dict[str, TRaw]) -> None:
        self._by_raw: dict[TRaw, EnumValue[TRaw]] = {}
        for name, raw_value in members.items():
            value = EnumValue(name=name, raw_value=raw_value)
            setattr(self, name, value)
            self._by_raw[raw_value] = value

    def from_raw(self, raw: TRaw) -> EnumValue[TRaw]:
        return self._by_raw.get(raw) or EnumValue(name="UNKNOWN", raw_value=raw)

    def is_unknown(self, value: EnumValue[TRaw]) -> bool:
        return value.raw_value not in self._by_raw


def create_enum(members: dict[str, TRaw]) -> EnumRegistry[TRaw]:
    return EnumRegistry(members)
