from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Iterator

from geodebug.models.enums import Certainty, FactState


@dataclass(frozen=True, slots=True)
class FactProvenance:
    origin: str
    method: str


@dataclass(frozen=True, slots=True)
class FactRecord:
    key: str
    state: FactState
    value: Any = None
    certainty: Certainty = Certainty.DETERMINISTIC
    provenance: FactProvenance | None = None
    sampled: bool = False
    sample_size: int | None = None

    @classmethod
    def known(
        cls,
        key: str,
        value: Any,
        *,
        certainty: Certainty = Certainty.DETERMINISTIC,
        provenance: FactProvenance | None = None,
        sampled: bool = False,
        sample_size: int | None = None,
    ) -> FactRecord:
        return cls(
            key=key,
            state=FactState.KNOWN,
            value=value,
            certainty=certainty,
            provenance=provenance,
            sampled=sampled,
            sample_size=sample_size,
        )

    @classmethod
    def unknown(
        cls,
        key: str,
        *,
        provenance: FactProvenance | None = None,
    ) -> FactRecord:
        return cls(key=key, state=FactState.UNKNOWN, provenance=provenance)


class DuplicateFactError(ValueError):
    pass


class FactStore:
    __slots__ = ("_records",)

    def __init__(self, records: Iterable[FactRecord] = ()) -> None:
        mapping: dict[str, FactRecord] = {}
        for record in records:
            if record.key in mapping:
                raise DuplicateFactError(f"duplicate fact key: {record.key}")
            mapping[record.key] = record
        self._records = mapping

    def __contains__(self, key: str) -> bool:
        return key in self._records

    def __iter__(self) -> Iterator[FactRecord]:
        for key in sorted(self._records):
            yield self._records[key]

    def get(self, key: str) -> FactRecord | None:
        return self._records.get(key)

    def require(self, key: str) -> FactRecord:
        try:
            return self._records[key]
        except KeyError as exc:
            raise KeyError(f"fact not found: {key}") from exc

    def with_fact(self, record: FactRecord) -> FactStore:
        if record.key in self._records:
            raise DuplicateFactError(f"duplicate fact key: {record.key}")
        return FactStore((*self._records.values(), record))
