from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

from geodebug.models.subjects import DatasetSnapshot


@dataclass(frozen=True, slots=True)
class InspectOptions:
    deep: bool = False


class AdapterError(RuntimeError):
    pass


class AdapterDependencyError(AdapterError):
    pass


class UnsupportedTargetError(AdapterError):
    pass


class Adapter(Protocol):
    name: str

    def supports(self, target: Any) -> int: ...

    def inspect(self, target: Any, options: InspectOptions) -> DatasetSnapshot: ...


def path_subject_id(path: Path) -> str:
    return f"file:{path.as_posix()}"
