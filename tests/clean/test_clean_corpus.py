from pyproj import CRS, Transformer

from geodebug import evaluate
from geodebug.facts.crs import build_crs_facts
from geodebug.facts.keys import (
    RASTER_NODATA_COLLISION_BANDS,
    RASTER_RESOLUTION,
    RASTER_TRANSFORM,
    SPATIAL_BOUNDS,
    VECTOR_INVALID_GEOMETRY_COUNT,
)
from geodebug.models.context import EvaluationContext
from geodebug.models.enums import FactState, SubjectKind
from geodebug.models.facts import FactRecord, FactStore
from geodebug.models.subjects import DatasetSnapshot, SubjectRef


def test_clean_geographic_vector_is_quiet() -> None:
    snapshot = DatasetSnapshot(
        subject=SubjectRef(id="vector:clean", kind=SubjectKind.VECTOR, adapter="test"),
        facts=FactStore(
            (
                *build_crs_facts("OGC:CRS84", origin="test", method="clean"),
                FactRecord.known(SPATIAL_BOUNDS, (103.0, 1.0, 104.0, 2.0)),
                FactRecord.known(VECTOR_INVALID_GEOMETRY_COUNT, 0),
            )
        ),
    )

    report = evaluate(EvaluationContext(subjects=(snapshot,)))

    assert report.diagnostics == []


def test_clean_projected_raster_is_quiet() -> None:
    crs = CRS.from_epsg(32648)
    transformer = Transformer.from_crs("OGC:CRS84", crs, always_xy=True)
    x, y = transformer.transform(103.8, 1.3)
    snapshot = DatasetSnapshot(
        subject=SubjectRef(id="raster:clean", kind=SubjectKind.RASTER, adapter="test"),
        facts=FactStore(
            (
                *build_crs_facts(crs.to_wkt(), origin="test", method="clean"),
                FactRecord.known(
                    SPATIAL_BOUNDS,
                    (x - 1000.0, y - 1000.0, x + 1000.0, y + 1000.0),
                ),
                FactRecord.known(RASTER_RESOLUTION, (10.0, 10.0)),
                FactRecord.known(
                    RASTER_TRANSFORM,
                    (10.0, 0.0, x - 1000.0, 0.0, -10.0, y + 1000.0),
                ),
                FactRecord(
                    key=RASTER_NODATA_COLLISION_BANDS,
                    state=FactState.NOT_APPLICABLE,
                ),
            )
        ),
    )

    report = evaluate(EvaluationContext(subjects=(snapshot,)))

    assert report.diagnostics == []
