from __future__ import annotations

from typing import Any

from geodebug.adapters.base import Adapter, InspectOptions, UnsupportedTargetError
from geodebug.models.subjects import DatasetSnapshot


class AdapterRegistry:
    def __init__(self) -> None:
        self._adapters: list[Adapter] = []

    def register(self, adapter: Adapter) -> None:
        self._adapters.append(adapter)

    def select(self, target: Any) -> Adapter:
        candidates = [(adapter.supports(target), adapter) for adapter in self._adapters]
        candidates = [(score, adapter) for score, adapter in candidates if score > 0]
        if not candidates:
            raise UnsupportedTargetError(f"no adapter supports target: {target!r}")
        candidates.sort(key=lambda item: item[0], reverse=True)
        return candidates[0][1]

    def inspect(
        self,
        target: Any,
        *,
        options: InspectOptions | None = None,
    ) -> DatasetSnapshot:
        adapter = self.select(target)
        return adapter.inspect(target, options or InspectOptions())
