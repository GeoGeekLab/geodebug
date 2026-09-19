from dataclasses import dataclass

from geodebug.models.enums import SubjectKind
from geodebug.models.facts import FactStore


@dataclass(frozen=True, slots=True)
class SubjectRef:
    id: str
    kind: SubjectKind
    uri: str | None = None
    label: str | None = None
    adapter: str | None = None


@dataclass(frozen=True, slots=True)
class DatasetSnapshot:
    subject: SubjectRef
    facts: FactStore
