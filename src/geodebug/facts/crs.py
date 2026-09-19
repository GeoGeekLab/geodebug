from __future__ import annotations

from typing import Any

from pyproj import CRS
from pyproj.exceptions import CRSError

from geodebug.facts.keys import (
    CRS_AREA_OF_USE_BOUNDS,
    CRS_AREA_OF_USE_NAME,
    CRS_AUTHORITY,
    CRS_AXIS_UNITS,
    CRS_CODE,
    CRS_KIND,
    CRS_PRESENT,
    CRS_WKT,
)
from geodebug.models.facts import FactProvenance, FactRecord


def build_crs_facts(
    value: Any,
    *,
    origin: str,
    method: str,
) -> tuple[FactRecord, ...]:
    provenance = FactProvenance(origin=origin, method=method)
    if value is None:
        return _unknown_crs_facts(
            provenance,
            present=False,
        )

    try:
        crs = CRS.from_user_input(value)
    except (CRSError, TypeError, ValueError):
        return _unknown_crs_facts(
            provenance,
            present=True,
        )

    authority = crs.to_authority()
    kind = (
        "geographic"
        if crs.is_geographic
        else "projected"
        if crs.is_projected
        else "geocentric"
        if crs.is_geocentric
        else "other"
    )
    records = [
        FactRecord.known(CRS_PRESENT, True, provenance=provenance),
        FactRecord.known(CRS_WKT, crs.to_wkt(), provenance=provenance),
        FactRecord.known(CRS_KIND, kind, provenance=provenance),
        FactRecord.known(
            CRS_AXIS_UNITS,
            tuple(axis.unit_name or "unknown" for axis in crs.axis_info),
            provenance=provenance,
        ),
    ]

    area = crs.area_of_use
    if area is None:
        records.extend(
            (
                FactRecord.unknown(CRS_AREA_OF_USE_BOUNDS, provenance=provenance),
                FactRecord.unknown(CRS_AREA_OF_USE_NAME, provenance=provenance),
            )
        )
    else:
        records.extend(
            (
                FactRecord.known(
                    CRS_AREA_OF_USE_BOUNDS,
                    (
                        float(area.west),
                        float(area.south),
                        float(area.east),
                        float(area.north),
                    ),
                    provenance=provenance,
                ),
                FactRecord.known(
                    CRS_AREA_OF_USE_NAME,
                    area.name,
                    provenance=provenance,
                ),
            )
        )

    if authority is None:
        records.extend(
            (
                FactRecord.unknown(CRS_AUTHORITY, provenance=provenance),
                FactRecord.unknown(CRS_CODE, provenance=provenance),
            )
        )
    else:
        records.extend(
            (
                FactRecord.known(CRS_AUTHORITY, authority[0], provenance=provenance),
                FactRecord.known(CRS_CODE, authority[1], provenance=provenance),
            )
        )
    return tuple(records)


def _unknown_crs_facts(
    provenance: FactProvenance,
    *,
    present: bool,
) -> tuple[FactRecord, ...]:
    return (
        FactRecord.known(CRS_PRESENT, present, provenance=provenance),
        FactRecord.unknown(CRS_WKT, provenance=provenance),
        FactRecord.unknown(CRS_KIND, provenance=provenance),
        FactRecord.unknown(CRS_AXIS_UNITS, provenance=provenance),
        FactRecord.unknown(CRS_AREA_OF_USE_BOUNDS, provenance=provenance),
        FactRecord.unknown(CRS_AREA_OF_USE_NAME, provenance=provenance),
        FactRecord.unknown(CRS_AUTHORITY, provenance=provenance),
        FactRecord.unknown(CRS_CODE, provenance=provenance),
    )
