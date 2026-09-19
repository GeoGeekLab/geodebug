from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from shapely.geometry import shape
from shapely.geometry.base import BaseGeometry

from geodebug.adapters.base import AdapterError, InspectOptions, path_subject_id
from geodebug.facts.crs import build_crs_facts
from geodebug.facts.keys import (
    SPATIAL_BOUNDS,
    VECTOR_EMPTY_GEOMETRY_COUNT,
    VECTOR_GEOMETRY_COUNT,
    VECTOR_GEOMETRY_TYPES,
    VECTOR_INVALID_GEOMETRY_COUNT,
)
from geodebug.models.enums import SubjectKind
from geodebug.models.facts import FactProvenance, FactRecord, FactStore
from geodebug.models.subjects import DatasetSnapshot, SubjectRef


class GeoJSONAdapter:
    name = "geojson"

    def supports(self, target: Any) -> int:
        if not isinstance(target, (str, Path)):
            return 0
        suffix = Path(target).suffix.casefold()
        return 100 if suffix in {".geojson", ".json"} else 0

    def inspect(self, target: Any, options: InspectOptions) -> DatasetSnapshot:
        path = Path(target)
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise AdapterError(f"unable to read GeoJSON: {path}") from exc

        geometries = _geometries(payload)
        provenance = FactProvenance(origin=self.name, method="geojson")
        records = list(build_crs_facts("OGC:CRS84", origin=self.name, method="rfc7946"))
        records.extend(_geometry_facts(geometries, provenance=provenance, deep=options.deep))
        bounds = _total_bounds(geometries)
        if bounds is None:
            records.append(FactRecord.unknown(SPATIAL_BOUNDS, provenance=provenance))
        else:
            records.append(FactRecord.known(SPATIAL_BOUNDS, bounds, provenance=provenance))

        return DatasetSnapshot(
            subject=SubjectRef(
                id=path_subject_id(path),
                kind=SubjectKind.VECTOR,
                uri=path.as_posix(),
                label=path.name,
                adapter=self.name,
            ),
            facts=FactStore(records),
        )


def _geometries(payload: Any) -> list[BaseGeometry]:
    if not isinstance(payload, dict):
        raise AdapterError("GeoJSON root must be an object")

    object_type = payload.get("type")
    raw: list[Any]
    if object_type == "FeatureCollection":
        features = payload.get("features")
        if not isinstance(features, list):
            raise AdapterError("GeoJSON FeatureCollection must contain a features array")
        raw = [feature.get("geometry") for feature in features if isinstance(feature, dict)]
    elif object_type == "Feature":
        raw = [payload.get("geometry")]
    else:
        raw = [payload]

    geometries: list[BaseGeometry] = []
    for item in raw:
        if item is None:
            continue
        try:
            geometries.append(shape(item))
        except (AttributeError, TypeError, ValueError) as exc:
            raise AdapterError("GeoJSON contains an invalid geometry object") from exc
    return geometries


def _geometry_facts(
    geometries: list[BaseGeometry],
    *,
    provenance: FactProvenance,
    deep: bool,
) -> tuple[FactRecord, ...]:
    count = len(geometries)
    empty_count = sum(geometry.is_empty for geometry in geometries)
    geometry_types = tuple(sorted({geometry.geom_type for geometry in geometries}))
    records = [
        FactRecord.known(VECTOR_GEOMETRY_COUNT, count, provenance=provenance),
        FactRecord.known(VECTOR_EMPTY_GEOMETRY_COUNT, empty_count, provenance=provenance),
        FactRecord.known(VECTOR_GEOMETRY_TYPES, geometry_types, provenance=provenance),
    ]
    if deep:
        records.append(
            FactRecord.known(
                VECTOR_INVALID_GEOMETRY_COUNT,
                sum(not geometry.is_valid for geometry in geometries),
                provenance=provenance,
            )
        )
    else:
        records.append(FactRecord.unknown(VECTOR_INVALID_GEOMETRY_COUNT, provenance=provenance))
    return tuple(records)


def _total_bounds(geometries: list[BaseGeometry]) -> tuple[float, float, float, float] | None:
    non_empty = [geometry for geometry in geometries if not geometry.is_empty]
    if not non_empty:
        return None
    xmin = min(geometry.bounds[0] for geometry in non_empty)
    ymin = min(geometry.bounds[1] for geometry in non_empty)
    xmax = max(geometry.bounds[2] for geometry in non_empty)
    ymax = max(geometry.bounds[3] for geometry in non_empty)
    return (float(xmin), float(ymin), float(xmax), float(ymax))
