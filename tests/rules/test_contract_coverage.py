from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from pyproj import CRS, Transformer

from geodebug.engine.defaults import build_default_registry
from geodebug.facts.crs import build_crs_facts
from geodebug.facts.keys import (
    CRS_AREA_OF_USE_BOUNDS,
    CRS_AXIS_UNITS,
    CRS_KIND,
    CRS_PRESENT,
    RASTER_NODATA_COLLISION_BANDS,
    RASTER_TRANSFORM,
    RELATION_BOUNDS_OVERLAP,
    RELATION_GRID_ALIGNED,
    SPATIAL_BOUNDS,
    VECTOR_INVALID_GEOMETRY_COUNT,
)
from geodebug.models.context import EvaluationContext
from geodebug.models.enums import FactState, RuleState, SubjectKind
from geodebug.models.facts import FactRecord, FactStore
from geodebug.models.operations import OperationContext
from geodebug.models.subjects import DatasetSnapshot, SubjectRef
from geodebug.rules.base import Rule


DOCS = Path(__file__).parents[2] / "docs" / "rules"


def _snapshot(
    *,
    kind: SubjectKind = SubjectKind.DATASET,
    facts: tuple[FactRecord, ...] = (),
    subject_id: str = "subject:test",
) -> DatasetSnapshot:
    return DatasetSnapshot(
        subject=SubjectRef(id=subject_id, kind=kind, adapter="test"),
        facts=FactStore(facts),
    )


def _context(
    *,
    kind: SubjectKind = SubjectKind.DATASET,
    facts: tuple[FactRecord, ...] = (),
    operation: OperationContext | None = None,
) -> EvaluationContext:
    return EvaluationContext(
        subjects=(_snapshot(kind=kind, facts=facts),),
        operation=operation,
    )


def _two_subject_context(*facts: FactRecord) -> EvaluationContext:
    return EvaluationContext(
        subjects=(
            _snapshot(subject_id="left"),
            _snapshot(subject_id="right"),
        ),
        facts=FactStore(facts),
    )


def _utm_context(lon: float, lat: float) -> EvaluationContext:
    crs = CRS.from_epsg(32648)
    transformer = Transformer.from_crs("OGC:CRS84", crs, always_xy=True)
    x, y = transformer.transform(lon, lat)
    return _context(
        facts=(
            *build_crs_facts(crs.to_wkt(), origin="test", method="contract"),
            FactRecord.known(
                SPATIAL_BOUNDS,
                (x - 1000.0, y - 1000.0, x + 1000.0, y + 1000.0),
            ),
        )
    )


def _geo_operation(name: str, *, with_units: bool = True) -> EvaluationContext:
    facts = [FactRecord.known(CRS_KIND, "geographic")]
    if with_units:
        facts.append(FactRecord.known(CRS_AXIS_UNITS, ("degree", "degree")))
    return _context(
        facts=tuple(facts),
        operation=OperationContext(
            name=name,
            parameters={"distance": 500} if name == "buffer" else {},
        ),
    )


def _projected_operation(name: str) -> EvaluationContext:
    return _context(
        facts=(
            FactRecord.known(CRS_KIND, "projected"),
            FactRecord.known(CRS_AXIS_UNITS, ("metre", "metre")),
        ),
        operation=OperationContext(
            name=name,
            parameters={"distance": 500} if name == "buffer" else {},
        ),
    )


def _contracts() -> dict[str, dict[RuleState, Callable[[], EvaluationContext]]]:
    return {
        "GEO101": {
            RuleState.PASS: lambda: _context(facts=(FactRecord.known(CRS_PRESENT, True),)),
            RuleState.FAIL: lambda: _context(facts=(FactRecord.known(CRS_PRESENT, False),)),
            RuleState.UNKNOWN: lambda: _context(facts=(FactRecord.unknown(CRS_PRESENT),)),
            RuleState.NOT_APPLICABLE: lambda: EvaluationContext(subjects=()),
        },
        "GEO103": {
            RuleState.PASS: lambda: _context(
                facts=(
                    FactRecord.known(CRS_KIND, "geographic"),
                    FactRecord.known(SPATIAL_BOUNDS, (103.0, 1.0, 104.0, 2.0)),
                )
            ),
            RuleState.FAIL: lambda: _context(
                facts=(
                    FactRecord.known(CRS_KIND, "geographic"),
                    FactRecord.known(SPATIAL_BOUNDS, (0.0, 91.0, 1.0, 92.0)),
                )
            ),
            RuleState.UNKNOWN: lambda: _context(
                facts=(
                    FactRecord.known(CRS_KIND, "geographic"),
                    FactRecord.unknown(SPATIAL_BOUNDS),
                )
            ),
            RuleState.NOT_APPLICABLE: lambda: _context(
                facts=(FactRecord.known(CRS_KIND, "projected"),)
            ),
        },
        "GEO105": {
            RuleState.PASS: lambda: _utm_context(103.8, 1.3),
            RuleState.FAIL: lambda: _utm_context(120.0, 1.3),
            RuleState.UNKNOWN: lambda: _context(
                facts=(
                    FactRecord.known(CRS_KIND, "projected"),
                    FactRecord.unknown(CRS_AREA_OF_USE_BOUNDS),
                    FactRecord.unknown(SPATIAL_BOUNDS),
                )
            ),
            RuleState.NOT_APPLICABLE: lambda: _context(
                facts=(FactRecord.known(CRS_KIND, "geographic"),)
            ),
        },
        "GEO201": {
            RuleState.PASS: lambda: _context(
                kind=SubjectKind.VECTOR,
                facts=(FactRecord.known(VECTOR_INVALID_GEOMETRY_COUNT, 0),),
            ),
            RuleState.FAIL: lambda: _context(
                kind=SubjectKind.VECTOR,
                facts=(FactRecord.known(VECTOR_INVALID_GEOMETRY_COUNT, 1),),
            ),
            RuleState.UNKNOWN: lambda: _context(
                kind=SubjectKind.VECTOR,
                facts=(FactRecord.unknown(VECTOR_INVALID_GEOMETRY_COUNT),),
            ),
            RuleState.NOT_APPLICABLE: lambda: _context(kind=SubjectKind.RASTER),
        },
        "GEO301": {
            RuleState.PASS: lambda: _context(
                kind=SubjectKind.RASTER,
                facts=(
                    FactRecord.known(
                        RASTER_TRANSFORM,
                        (10.0, 0.0, 0.0, 0.0, -10.0, 100.0),
                    ),
                ),
            ),
            RuleState.FAIL: lambda: _context(
                kind=SubjectKind.RASTER,
                facts=(
                    FactRecord.known(
                        RASTER_TRANSFORM,
                        (0.0, 0.0, 0.0, 0.0, 0.0, 100.0),
                    ),
                ),
            ),
            RuleState.UNKNOWN: lambda: _context(
                kind=SubjectKind.RASTER,
                facts=(FactRecord.unknown(RASTER_TRANSFORM),),
            ),
            RuleState.NOT_APPLICABLE: lambda: _context(kind=SubjectKind.VECTOR),
        },
        "GEO304": {
            RuleState.PASS: lambda: _context(
                kind=SubjectKind.RASTER,
                facts=(FactRecord.known(RASTER_NODATA_COLLISION_BANDS, ()),),
            ),
            RuleState.FAIL: lambda: _context(
                kind=SubjectKind.RASTER,
                facts=(FactRecord.known(RASTER_NODATA_COLLISION_BANDS, (1,)),),
            ),
            RuleState.UNKNOWN: lambda: _context(
                kind=SubjectKind.RASTER,
                facts=(FactRecord.unknown(RASTER_NODATA_COLLISION_BANDS),),
            ),
            RuleState.NOT_APPLICABLE: lambda: _context(kind=SubjectKind.VECTOR),
        },
        "GEO402": {
            RuleState.PASS: lambda: _two_subject_context(
                FactRecord.known(RELATION_BOUNDS_OVERLAP, True)
            ),
            RuleState.FAIL: lambda: _two_subject_context(
                FactRecord.known(RELATION_BOUNDS_OVERLAP, False)
            ),
            RuleState.UNKNOWN: lambda: _two_subject_context(
                FactRecord.unknown(RELATION_BOUNDS_OVERLAP)
            ),
            RuleState.NOT_APPLICABLE: lambda: _context(),
        },
        "GEO404": {
            RuleState.PASS: lambda: _two_subject_context(
                FactRecord.known(RELATION_GRID_ALIGNED, True)
            ),
            RuleState.FAIL: lambda: _two_subject_context(
                FactRecord.known(RELATION_GRID_ALIGNED, False)
            ),
            RuleState.UNKNOWN: lambda: _two_subject_context(
                FactRecord.unknown(RELATION_GRID_ALIGNED)
            ),
            RuleState.NOT_APPLICABLE: lambda: _two_subject_context(
                FactRecord(
                    key=RELATION_GRID_ALIGNED,
                    state=FactState.NOT_APPLICABLE,
                )
            ),
        },
        "GEO501": {
            RuleState.PASS: lambda: _projected_operation("buffer"),
            RuleState.FAIL: lambda: _geo_operation("buffer"),
            RuleState.UNKNOWN: lambda: _geo_operation("buffer", with_units=False),
            RuleState.NOT_APPLICABLE: lambda: _geo_operation("clip"),
        },
        "GEO502": {
            RuleState.PASS: lambda: _projected_operation("area"),
            RuleState.FAIL: lambda: _geo_operation("area"),
            RuleState.UNKNOWN: lambda: _geo_operation("area", with_units=False),
            RuleState.NOT_APPLICABLE: lambda: _geo_operation("buffer"),
        },
        "GEO503": {
            RuleState.PASS: lambda: _projected_operation("distance"),
            RuleState.FAIL: lambda: _geo_operation("distance"),
            RuleState.UNKNOWN: lambda: _geo_operation("distance", with_units=False),
            RuleState.NOT_APPLICABLE: lambda: _geo_operation("area"),
        },
    }


def test_every_registered_rule_has_documentation_and_contract() -> None:
    registry = build_default_registry()
    rule_ids = {rule.spec.id for rule in registry.all()}

    assert set(_contracts()) == rule_ids
    assert {path.stem for path in DOCS.glob("GEO*.md")} == rule_ids


def test_every_rule_exercises_all_four_states() -> None:
    expected_states = {
        RuleState.PASS,
        RuleState.FAIL,
        RuleState.UNKNOWN,
        RuleState.NOT_APPLICABLE,
    }

    for rule in build_default_registry().all():
        cases = _contracts()[rule.spec.id]
        assert set(cases) == expected_states
        for expected, factory in cases.items():
            result = _evaluate(rule, factory())
            assert result is expected, f"{rule.spec.id}: expected {expected}, got {result}"


def _evaluate(rule: Rule, context: EvaluationContext) -> RuleState:
    return rule.evaluate(context).state
