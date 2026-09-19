import pytest

from geodebug.facts.keys import CRS_AXIS_UNITS, CRS_KIND
from geodebug.models.enums import RuleState
from geodebug.models.facts import FactRecord
from geodebug.models.operations import OperationContext
from geodebug.rules.operations.geo501 import AngularCRSBufferRule


@pytest.mark.parametrize(
    ("crs_kind", "units", "operation", "expected"),
    [
        (
            FactRecord.known(CRS_KIND, "geographic"),
            FactRecord.known(CRS_AXIS_UNITS, ("degree", "degree")),
            OperationContext(name="buffer", parameters={"distance": 500}),
            RuleState.FAIL,
        ),
        (
            FactRecord.known(CRS_KIND, "projected"),
            FactRecord.known(CRS_AXIS_UNITS, ("metre", "metre")),
            OperationContext(name="buffer", parameters={"distance": 500}),
            RuleState.PASS,
        ),
        (
            FactRecord.unknown(CRS_KIND),
            FactRecord.unknown(CRS_AXIS_UNITS),
            OperationContext(name="buffer", parameters={"distance": 500}),
            RuleState.UNKNOWN,
        ),
        (
            FactRecord.known(CRS_KIND, "geographic"),
            FactRecord.known(CRS_AXIS_UNITS, ("degree", "degree")),
            OperationContext(name="clip"),
            RuleState.NOT_APPLICABLE,
        ),
    ],
)
def test_geo501_truth_table(make_context, crs_kind, units, operation, expected) -> None:
    context = make_context(facts=[crs_kind, units], operation=operation)

    assert AngularCRSBufferRule().evaluate(context).state is expected
