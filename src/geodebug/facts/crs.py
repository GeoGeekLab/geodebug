from __future__ import annotations

from typing import Any

from pyproj import CRS
from pyproj.exceptions import CRSError

from geodebug.facts.keys import (
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
        return (
            FactRecord.known(CRS_PRESENT, False, provenance=provenance),
            FactRecord.unknown(CRS_WKT, provenance=provenance),
            FactRecord.unknown(CRS_KIND, provenance=provenance),
            FactRecord.unknown(CRS_AXIS_UNITS, provenance=provenance),
        )

    try:
        crs = CRS.from_user_input(value)
    except (CRSError, TypeError, ValueError):
        return (
            FactRecord.known(CRS_PRESENT, True, provenance=provenance),
            FactRecord.unknown(CRS_WKT, provenance=provenance),
            FactRecord.unknown(CRS_KIND, provenance=provenance),
            FactRecord.unknown(CRS_AXIS_UNITS, provenance=provenance),
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
