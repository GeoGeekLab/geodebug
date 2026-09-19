from __future__ import annotations

import math
from typing import TypeGuard

from pyproj import CRS, Transformer
from pyproj.exceptions import CRSError, ProjError

from geodebug.facts.keys import (
    CRS_WKT,
    RASTER_RESOLUTION,
    RASTER_TRANSFORM,
    RELATION_BOUNDS_OVERLAP,
    RELATION_GRID_ALIGNED,
    RELATION_GRID_OFFSET_PIXELS,
    RELATION_OVERLAP_RATIO,
    SPATIAL_BOUNDS,
)
from geodebug.models.enums import FactState, SubjectKind
from geodebug.models.facts import FactProvenance, FactRecord, FactStore
from geodebug.models.subjects import DatasetSnapshot


Bounds = tuple[float, float, float, float]
Pair = tuple[float, float]
Transform6 = tuple[float, float, float, float, float, float]


def build_relation_facts(left: DatasetSnapshot, right: DatasetSnapshot) -> FactStore:
    provenance = FactProvenance(origin="geodebug", method="relation")
    records = list(_bounds_relation(left, right, provenance=provenance))
    records.extend(_grid_relation(left, right, provenance=provenance))
    return FactStore(records)


def _known(snapshot: DatasetSnapshot, key: str) -> object | None:
    fact = snapshot.facts.get(key)
    if fact is None or fact.state is not FactState.KNOWN:
        return None
    return fact.value


def _bounds_relation(
    left: DatasetSnapshot,
    right: DatasetSnapshot,
    *,
    provenance: FactProvenance,
) -> tuple[FactRecord, ...]:
    left_bounds = _as_bounds(_known(left, SPATIAL_BOUNDS))
    right_bounds = _as_bounds(_known(right, SPATIAL_BOUNDS))
    left_wkt = _known(left, CRS_WKT)
    right_wkt = _known(right, CRS_WKT)
    if (
        left_bounds is None
        or right_bounds is None
        or not isinstance(left_wkt, str)
        or not isinstance(right_wkt, str)
    ):
        return (
            FactRecord.unknown(RELATION_BOUNDS_OVERLAP, provenance=provenance),
            FactRecord.unknown(RELATION_OVERLAP_RATIO, provenance=provenance),
        )

    transformed = _transform_bounds(right_bounds, right_wkt, left_wkt)
    if transformed is None:
        return (
            FactRecord.unknown(RELATION_BOUNDS_OVERLAP, provenance=provenance),
            FactRecord.unknown(RELATION_OVERLAP_RATIO, provenance=provenance),
        )

    lx0, ly0, lx1, ly1 = left_bounds
    rx0, ry0, rx1, ry1 = transformed
    overlaps = max(lx0, rx0) <= min(lx1, rx1) and max(ly0, ry0) <= min(ly1, ry1)

    intersection_width = max(0.0, min(lx1, rx1) - max(lx0, rx0))
    intersection_height = max(0.0, min(ly1, ry1) - max(ly0, ry0))
    intersection_area = intersection_width * intersection_height
    left_area = max(0.0, lx1 - lx0) * max(0.0, ly1 - ly0)
    right_area = max(0.0, rx1 - rx0) * max(0.0, ry1 - ry0)
    denominator = min(left_area, right_area)

    ratio = intersection_area / denominator if denominator > 0.0 else None
    ratio_fact = (
        FactRecord.known(RELATION_OVERLAP_RATIO, float(ratio), provenance=provenance)
        if ratio is not None
        else FactRecord.unknown(RELATION_OVERLAP_RATIO, provenance=provenance)
    )
    return (
        FactRecord.known(RELATION_BOUNDS_OVERLAP, overlaps, provenance=provenance),
        ratio_fact,
    )


def _grid_relation(
    left: DatasetSnapshot,
    right: DatasetSnapshot,
    *,
    provenance: FactProvenance,
) -> tuple[FactRecord, ...]:
    if left.subject.kind is not SubjectKind.RASTER or right.subject.kind is not SubjectKind.RASTER:
        return (
            FactRecord(
                key=RELATION_GRID_ALIGNED,
                state=FactState.NOT_APPLICABLE,
                provenance=provenance,
            ),
            FactRecord(
                key=RELATION_GRID_OFFSET_PIXELS,
                state=FactState.NOT_APPLICABLE,
                provenance=provenance,
            ),
        )

    left_wkt = _known(left, CRS_WKT)
    right_wkt = _known(right, CRS_WKT)
    left_resolution = _as_pair(_known(left, RASTER_RESOLUTION))
    right_resolution = _as_pair(_known(right, RASTER_RESOLUTION))
    left_transform = _as_transform(_known(left, RASTER_TRANSFORM))
    right_transform = _as_transform(_known(right, RASTER_TRANSFORM))
    if (
        not isinstance(left_wkt, str)
        or not isinstance(right_wkt, str)
        or left_resolution is None
        or right_resolution is None
        or left_transform is None
        or right_transform is None
    ):
        return _unknown_grid(provenance)

    try:
        if CRS.from_wkt(left_wkt) != CRS.from_wkt(right_wkt):
            return _unknown_grid(provenance)
    except CRSError:
        return _unknown_grid(provenance)

    if not (
        math.isclose(left_resolution[0], right_resolution[0], rel_tol=1e-9, abs_tol=1e-12)
        and math.isclose(left_resolution[1], right_resolution[1], rel_tol=1e-9, abs_tol=1e-12)
    ):
        return _unknown_grid(provenance)

    if any(
        not math.isclose(value, 0.0, abs_tol=1e-12)
        for value in (left_transform[1], left_transform[3], right_transform[1], right_transform[3])
    ):
        return _unknown_grid(provenance)

    xres, yres = left_resolution
    if xres <= 0.0 or yres <= 0.0:
        return _unknown_grid(provenance)

    x_offset = (right_transform[2] - left_transform[2]) / xres
    y_offset = (right_transform[5] - left_transform[5]) / yres
    x_fraction = x_offset - round(x_offset)
    y_fraction = y_offset - round(y_offset)
    aligned = math.isclose(x_fraction, 0.0, abs_tol=1e-9) and math.isclose(
        y_fraction, 0.0, abs_tol=1e-9
    )
    return (
        FactRecord.known(RELATION_GRID_ALIGNED, aligned, provenance=provenance),
        FactRecord.known(
            RELATION_GRID_OFFSET_PIXELS,
            (float(x_fraction), float(y_fraction)),
            provenance=provenance,
        ),
    )


def _transform_bounds(bounds: Bounds, source_wkt: str, target_wkt: str) -> Bounds | None:
    try:
        source = CRS.from_wkt(source_wkt)
        target = CRS.from_wkt(target_wkt)
        if source == target:
            return bounds
        transformer = Transformer.from_crs(source, target, always_xy=True)
        transformed = transformer.transform_bounds(*bounds, densify_pts=21)
    except (CRSError, ProjError, ValueError):
        return None
    if not all(math.isfinite(value) for value in transformed):
        return None
    return (
        float(transformed[0]),
        float(transformed[1]),
        float(transformed[2]),
        float(transformed[3]),
    )


def _unknown_grid(provenance: FactProvenance) -> tuple[FactRecord, ...]:
    return (
        FactRecord.unknown(RELATION_GRID_ALIGNED, provenance=provenance),
        FactRecord.unknown(RELATION_GRID_OFFSET_PIXELS, provenance=provenance),
    )


def _numbers(value: object, length: int) -> tuple[float, ...] | None:
    if not isinstance(value, (list, tuple)) or len(value) != length:
        return None
    numbers: list[float] = []
    for item in value:
        if not isinstance(item, (int, float)) or not math.isfinite(item):
            return None
        numbers.append(float(item))
    return tuple(numbers)


def _as_pair(value: object) -> Pair | None:
    numbers = _numbers(value, 2)
    if numbers is None:
        return None
    return (numbers[0], numbers[1])


def _as_transform(value: object) -> Transform6 | None:
    numbers = _numbers(value, 6)
    if numbers is None:
        return None
    return (
        numbers[0],
        numbers[1],
        numbers[2],
        numbers[3],
        numbers[4],
        numbers[5],
    )


def _as_bounds(value: object) -> Bounds | None:
    numbers = _numbers(value, 4)
    if numbers is None:
        return None
    return (numbers[0], numbers[1], numbers[2], numbers[3])
