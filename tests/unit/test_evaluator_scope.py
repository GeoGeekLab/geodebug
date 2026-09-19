from geodebug.engine.defaults import build_default_registry
from geodebug.engine.evaluator import Evaluator
from geodebug.facts.keys import CRS_PRESENT
from geodebug.models.context import EvaluationContext
from geodebug.models.enums import SubjectKind
from geodebug.models.facts import FactRecord, FactStore
from geodebug.models.subjects import DatasetSnapshot, SubjectRef


def _snapshot(subject_id: str, crs_present: bool) -> DatasetSnapshot:
    return DatasetSnapshot(
        subject=SubjectRef(id=subject_id, kind=SubjectKind.VECTOR, adapter="test"),
        facts=FactStore([FactRecord.known(CRS_PRESENT, crs_present)]),
    )


def test_dataset_rules_are_evaluated_per_subject() -> None:
    context = EvaluationContext(
        subjects=(
            _snapshot("left", False),
            _snapshot("right", True),
        )
    )

    report = Evaluator(build_default_registry()).evaluate(context)

    diagnostic = next(item for item in report.diagnostics if item.rule_id == "GEO101")
    assert diagnostic.subject_ids == ["left"]
