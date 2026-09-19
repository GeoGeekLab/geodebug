import pytest

from geodebug.facts.keys import CRS_PRESENT
from geodebug.models.context import EvaluationContext
from geodebug.models.enums import RuleState
from geodebug.models.facts import FactRecord
from geodebug.rules.crs.geo101 import MissingCRSRule


@pytest.mark.parametrize(
    ("fact", "expected"),
    [
        (FactRecord.known(CRS_PRESENT, True), RuleState.PASS),
        (FactRecord.known(CRS_PRESENT, False), RuleState.FAIL),
        (FactRecord.unknown(CRS_PRESENT), RuleState.UNKNOWN),
    ],
)
def test_geo101_truth_table(make_context, fact, expected) -> None:
    result = MissingCRSRule().evaluate(make_context(facts=[fact]))

    assert result.state is expected


def test_geo101_without_subject_is_not_applicable() -> None:
    result = MissingCRSRule().evaluate(EvaluationContext(subjects=()))

    assert result.state is RuleState.NOT_APPLICABLE
