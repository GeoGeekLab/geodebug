import pytest

from geodebug.facts.keys import RASTER_NODATA_COLLISION_BANDS, RASTER_TRANSFORM
from geodebug.models.enums import FactState, RuleState, SubjectKind
from geodebug.models.facts import FactRecord
from geodebug.rules.raster.geo301 import InvalidRasterTransformRule
from geodebug.rules.raster.geo304 import NoDataMaskCollisionRule


@pytest.mark.parametrize(
    ("transform", "expected"),
    [
        ((10.0, 0.0, 0.0, 0.0, -10.0, 100.0), RuleState.PASS),
        ((0.0, 0.0, 0.0, 0.0, 0.0, 100.0), RuleState.FAIL),
    ],
)
def test_geo301_transform_determinant(make_context, transform, expected) -> None:
    context = make_context(
        kind=SubjectKind.RASTER,
        facts=[FactRecord.known(RASTER_TRANSFORM, transform)],
    )

    assert InvalidRasterTransformRule().evaluate(context).state is expected


@pytest.mark.parametrize(
    ("fact", "expected"),
    [
        (FactRecord.known(RASTER_NODATA_COLLISION_BANDS, ()), RuleState.PASS),
        (FactRecord.known(RASTER_NODATA_COLLISION_BANDS, (1,)), RuleState.FAIL),
        (FactRecord.unknown(RASTER_NODATA_COLLISION_BANDS), RuleState.UNKNOWN),
        (
            FactRecord(
                key=RASTER_NODATA_COLLISION_BANDS,
                state=FactState.NOT_APPLICABLE,
            ),
            RuleState.NOT_APPLICABLE,
        ),
    ],
)
def test_geo304_truth_table(make_context, fact, expected) -> None:
    context = make_context(kind=SubjectKind.RASTER, facts=[fact])

    assert NoDataMaskCollisionRule().evaluate(context).state is expected
