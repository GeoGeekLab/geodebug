from pyproj import CRS

from geodebug.facts.keys import (
    CRS_WKT,
    RASTER_RESOLUTION,
    RASTER_TRANSFORM,
    RELATION_GRID_ALIGNED,
    RELATION_GRID_OFFSET_PIXELS,
    SPATIAL_BOUNDS,
)
from geodebug.facts.relations import build_relation_facts
from geodebug.models.enums import SubjectKind
from geodebug.models.facts import FactRecord, FactStore
from geodebug.models.subjects import DatasetSnapshot, SubjectRef


def _raster(subject_id: str, origin_x: float) -> DatasetSnapshot:
    return DatasetSnapshot(
        subject=SubjectRef(id=subject_id, kind=SubjectKind.RASTER, adapter="test"),
        facts=FactStore(
            [
                FactRecord.known(CRS_WKT, CRS.from_epsg(32648).to_wkt()),
                FactRecord.known(SPATIAL_BOUNDS, (origin_x, 0.0, origin_x + 100.0, 100.0)),
                FactRecord.known(RASTER_RESOLUTION, (10.0, 10.0)),
                FactRecord.known(
                    RASTER_TRANSFORM,
                    (10.0, 0.0, origin_x, 0.0, -10.0, 100.0),
                ),
            ]
        ),
    )


def test_relation_facts_detect_half_pixel_grid_offset() -> None:
    facts = build_relation_facts(_raster("left", 0.0), _raster("right", 5.0))

    assert facts.require(RELATION_GRID_ALIGNED).value is False
    assert facts.require(RELATION_GRID_OFFSET_PIXELS).value == (0.5, 0.0)


def test_relation_facts_accept_integer_pixel_offset() -> None:
    facts = build_relation_facts(_raster("left", 0.0), _raster("right", 20.0))

    assert facts.require(RELATION_GRID_ALIGNED).value is True
