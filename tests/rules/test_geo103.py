import pytest

from geodebug.facts.keys import CRS_KIND, SPATIAL_BOUNDS
from geodebug.models.enums import RuleState
from geodebug.models.facts import FactRecord
from geodebug.rules.crs.geo103 import GeographicCoordinateRangeRule


@pytest.mark.parametrize(
    ("bounds", "expected"),
    [
        ((103.0, 1.0, 104.0, 2.0), RuleState.PASS),
        ((0.0, 91.0, 1.0, 92.0), RuleState.FAIL),
        ((361.0, 0.0, 362.0, 1.0), RuleState.FAIL),
    ],
)
def test_geo103_geographic_ranges(make_context, bounds, expected) -> None:
    context = make_context(
        facts=[
            FactRecord.known(CRS_KIND, "geographic"),
            FactRecord.known(SPATIAL_BOUNDS, bounds),
        ]
    )

    assert GeographicCoordinateRangeRule().evaluate(context).state is expected


def test_geo103_projected_crs_is_not_applicable(make_context) -> None:
    context = make_context(
        facts=[
            FactRecord.known(CRS_KIND, "projected"),
            FactRecord.known(SPATIAL_BOUNDS, (0, 0, 1000, 1000)),
        ]
    )

    assert GeographicCoordinateRangeRule().evaluate(context).state is RuleState.NOT_APPLICABLE
