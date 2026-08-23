"""
Generic forward-compatible enum factory -- see SDK_CAPABILITY_SPEC.md section 11.4. An unknown
raw value never raises: it becomes EnumValue(name='UNKNOWN', raw_value=raw), preserving the exact
value received (integer or string, depending on the real enum's Group -- see section 11.3).

Deliberately does NOT use the stdlib's enum.Enum/IntEnum: both raise ValueError for an unknown
value by default, the opposite of the forward-compatible behavior required by the brief.
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
    """Instance returned by create_enum -- attribute access (STATUS.COMPLETED) + from_raw()."""

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
