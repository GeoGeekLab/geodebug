from dataclasses import dataclass, field

from geodebug.models.facts import FactStore
from geodebug.models.operations import OperationContext
from geodebug.models.subjects import DatasetSnapshot


@dataclass(frozen=True, slots=True)
class EvaluationContext:
    subjects: tuple[DatasetSnapshot, ...]
    operation: OperationContext | None = None
    facts: FactStore = field(default_factory=FactStore)

    @property
    def primary(self) -> DatasetSnapshot | None:
        return self.subjects[0] if self.subjects else None
