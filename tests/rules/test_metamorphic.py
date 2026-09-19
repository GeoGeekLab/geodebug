from pyproj import CRS

from geodebug.facts.keys import (
    CRS_AXIS_UNITS,
    CRS_KIND,
    CRS_WKT,
    RASTER_RESOLUTION,
    RASTER_TRANSFORM,
    RELATION_GRID_ALIGNED,
    SPATIAL_BOUNDS,
)
from geodebug.facts.relations import build_relation_facts
from geodebug.models.context import EvaluationContext
from geodebug.models.enums import RuleState, SubjectKind
from geodebug.models.facts import FactRecord, FactStore
from geodebug.models.operations import OperationContext
from geodebug.models.subjects import DatasetSnapshot, SubjectRef
from geodebug.rules.crs.geo103 import GeographicCoordinateRangeRule
from geodebug.rules.operations.geo501 import AngularCRSBufferRule
from geodebug.rules.relations.geo404 import RasterGridMisalignmentRule


def _raster(subject_id: str, origin_x: float) -> DatasetSnapshot:
    return DatasetSnapshot(
        subject=SubjectRef(id=subject_id, kind=SubjectKind.RASTER, adapter="test"),
        facts=FactStore(
            (
                FactRecord.known(CRS_WKT, CRS.from_epsg(32648).to_wkt()),
                FactRecord.known(SPATIAL_BOUNDS, (origin_x, 0.0, origin_x + 100.0, 100.0)),
                FactRecord.known(RASTER_RESOLUTION, (10.0, 10.0)),
                FactRecord.known(
                    RASTER_TRANSFORM,
                    (10.0, 0.0, origin_x, 0.0, -10.0, 100.0),
                ),
            )
        ),
    )


def test_geo103_correction_removes_finding(make_context) -> None:
    invalid = make_context(
        facts=(
            FactRecord.known(CRS_KIND, "geographic"),
            FactRecord.known(SPATIAL_BOUNDS, (0.0, 91.0, 1.0, 92.0)),
        )
    )
    corrected = make_context(
        facts=(
            FactRecord.known(CRS_KIND, "geographic"),
            FactRecord.known(SPATIAL_BOUNDS, (0.0, 41.0, 1.0, 42.0)),
        )
    )

    rule = GeographicCoordinateRangeRule()
    assert rule.evaluate(invalid).state is RuleState.FAIL
    assert rule.evaluate(corrected).state is RuleState.PASS


def test_geo404_integer_pixel_shift_restores_alignment() -> None:
    left = _raster("left", 0.0)
    half_pixel = _raster("right", 5.0)
    integer_pixel = _raster("right", 20.0)
    rule = RasterGridMisalignmentRule()

    bad = EvaluationContext(
        subjects=(left, half_pixel),
        facts=build_relation_facts(left, half_pixel),
    )
    corrected = EvaluationContext(
        subjects=(left, integer_pixel),
        facts=build_relation_facts(left, integer_pixel),
    )

    assert bad.facts.require(RELATION_GRID_ALIGNED).value is False
    assert rule.evaluate(bad).state is RuleState.FAIL
    assert corrected.facts.require(RELATION_GRID_ALIGNED).value is True
    assert rule.evaluate(corrected).state is RuleState.PASS


def test_geo501_projection_changes_buffer_contract(make_context) -> None:
    geographic = make_context(
        facts=(
            FactRecord.known(CRS_KIND, "geographic"),
            FactRecord.known(CRS_AXIS_UNITS, ("degree", "degree")),
        ),
        operation=OperationContext(name="buffer", parameters={"distance": 500}),
    )
    projected = make_context(
        facts=(
            FactRecord.known(CRS_KIND, "projected"),
            FactRecord.known(CRS_AXIS_UNITS, ("metre", "metre")),
        ),
        operation=OperationContext(name="buffer", parameters={"distance": 500}),
    )

    rule = AngularCRSBufferRule()
    assert rule.evaluate(geographic).state is RuleState.FAIL
    assert rule.evaluate(projected).state is RuleState.PASS
