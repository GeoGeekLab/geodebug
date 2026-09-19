import pytest

from geodebug.facts.keys import CRS_AXIS_UNITS, CRS_KIND
from geodebug.models.enums import RuleState
from geodebug.models.facts import FactRecord
from geodebug.models.operations import OperationContext
from geodebug.rules.operations.geo502 import PlanarAreaOnGeographicCRSRule
from geodebug.rules.operations.geo503 import PlanarDistanceOnGeographicCRSRule


@pytest.mark.parametrize(
    ("rule", "operation"),
    [
        (PlanarAreaOnGeographicCRSRule(), "area"),
        (PlanarDistanceOnGeographicCRSRule(), "distance"),
        (PlanarDistanceOnGeographicCRSRule(), "length"),
    ],
)
def test_measurement_rules_fail_on_geographic_crs(make_context, rule, operation) -> None:
    context = make_context(
        facts=[
            FactRecord.known(CRS_KIND, "geographic"),
            FactRecord.known(CRS_AXIS_UNITS, ("degree", "degree")),
        ],
        operation=OperationContext(name=operation),
    )

    assert rule.evaluate(context).state is RuleState.FAIL


def test_area_rule_passes_on_projected_crs(make_context) -> None:
    context = make_context(
        facts=[
            FactRecord.known(CRS_KIND, "projected"),
            FactRecord.known(CRS_AXIS_UNITS, ("metre", "metre")),
        ],
        operation=OperationContext(name="area"),
    )

    assert PlanarAreaOnGeographicCRSRule().evaluate(context).state is RuleState.PASS
