from __future__ import annotations

import math

import pyproj


Bounds = tuple[float, float, float, float]


def transform_bounds(
    bounds: Bounds,
    source_wkt: str,
    target: str = "OGC:CRS84",
) -> Bounds | None:
    try:
        source = pyproj.CRS.from_wkt(source_wkt)
        target_crs = pyproj.CRS.from_user_input(target)
        if source == target_crs:
            return bounds
        transformer = pyproj.Transformer.from_crs(source, target_crs, always_xy=True)
        transformed = transformer.transform_bounds(*bounds, densify_pts=21)
    except (pyproj.exceptions.CRSError, pyproj.exceptions.ProjError, ValueError):
        return None

    if not all(math.isfinite(value) for value in transformed):
        return None
    return (
        float(transformed[0]),
        float(transformed[1]),
        float(transformed[2]),
        float(transformed[3]),
    )


def geographic_bounds_overlap(left: Bounds, right: Bounds) -> bool:
    if max(left[1], right[1]) > min(left[3], right[3]):
        return False

    left_intervals = _longitude_intervals(left[0], left[2])
    right_intervals = _longitude_intervals(right[0], right[2])
    return any(
        max(left_west, right_west) <= min(left_east, right_east)
        for left_west, left_east in left_intervals
        for right_west, right_east in right_intervals
    )


def _longitude_intervals(west: float, east: float) -> tuple[tuple[float, float], ...]:
    if west <= east:
        return ((west, east),)
    return ((west, 180.0), (-180.0, east))
