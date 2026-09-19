import pytest

from geodebug.facts.keys import VECTOR_GEOMETRY_COUNT, VECTOR_INVALID_GEOMETRY_COUNT
from geodebug.models.enums import RuleState, SubjectKind
from geodebug.models.facts import FactRecord
from geodebug.rules.vector.geo201 import InvalidGeometryRule


@pytest.mark.parametrize(
    ("fact", "expected"),
    [
        (FactRecord.known(VECTOR_INVALID_GEOMETRY_COUNT, 0), RuleState.PASS),
        (FactRecord.known(VECTOR_INVALID_GEOMETRY_COUNT, 2), RuleState.FAIL),
        (FactRecord.unknown(VECTOR_INVALID_GEOMETRY_COUNT), RuleState.UNKNOWN),
    ],
)
def test_geo201_truth_table(make_context, fact, expected) -> None:
    context = make_context(
        kind=SubjectKind.VECTOR,
        facts=[FactRecord.known(VECTOR_GEOMETRY_COUNT, 5), fact],
    )

    assert InvalidGeometryRule().evaluate(context).state is expected


def test_geo201_non_vector_is_not_applicable(make_context) -> None:
    result = InvalidGeometryRule().evaluate(make_context())

    assert result.state is RuleState.NOT_APPLICABLE
