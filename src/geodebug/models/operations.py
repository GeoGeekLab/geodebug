from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping


@dataclass(frozen=True, slots=True)
class OperationContext:
    name: str
    parameters: Mapping[str, Any] = field(default_factory=dict)
    source_path: str | None = None
    source_line: int | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "parameters", MappingProxyType(dict(self.parameters)))
