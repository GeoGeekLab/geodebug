from collections.abc import Iterable

import pytest

from geodebug.models.context import EvaluationContext
from geodebug.models.enums import SubjectKind
from geodebug.models.facts import FactRecord, FactStore
from geodebug.models.operations import OperationContext
from geodebug.models.subjects import DatasetSnapshot, SubjectRef


@pytest.fixture
def make_context():
    def factory(
        *,
        kind: SubjectKind = SubjectKind.DATASET,
        facts: Iterable[FactRecord] = (),
        operation: OperationContext | None = None,
    ) -> EvaluationContext:
        snapshot = DatasetSnapshot(
            subject=SubjectRef(id="subject:test", kind=kind, adapter="test"),
            facts=FactStore(facts),
        )
        return EvaluationContext(subjects=(snapshot,), operation=operation)

    return factory
