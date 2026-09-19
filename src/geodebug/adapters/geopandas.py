from __future__ import annotations

from typing import Any

from geodebug.adapters.base import AdapterDependencyError, InspectOptions
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


class GeoPandasAdapter:
    name = "geopandas"

    def supports(self, target: Any) -> int:
        try:
            import geopandas as gpd
        except ImportError:
            return 0
        return 110 if isinstance(target, gpd.GeoDataFrame) else 0

    def inspect(self, target: Any, options: InspectOptions) -> DatasetSnapshot:
        del options
        try:
            import geopandas as gpd
        except ImportError as exc:
            raise AdapterDependencyError(
                "GeoPandas support requires 'pip install geodebug[geopandas]'"
            ) from exc
        if not isinstance(target, gpd.GeoDataFrame):
            raise TypeError("GeoPandasAdapter requires a GeoDataFrame")

        geometry = target.geometry
        provenance = FactProvenance(origin=self.name, method="geodataframe")
        records = list(
            build_crs_facts(
                target.crs.to_wkt() if target.crs is not None else None,
                origin=self.name,
                method="geodataframe.crs",
            )
        )
        records.extend(
            (
                FactRecord.known(
                    VECTOR_GEOMETRY_COUNT,
                    len(target),
                    provenance=provenance,
                ),
                FactRecord.known(
                    VECTOR_INVALID_GEOMETRY_COUNT,
                    int((~geometry.is_valid & ~geometry.isna()).sum()),
                    provenance=provenance,
                ),
                FactRecord.known(
                    VECTOR_EMPTY_GEOMETRY_COUNT,
                    int(geometry.is_empty.sum()),
                    provenance=provenance,
                ),
                FactRecord.known(
                    VECTOR_GEOMETRY_TYPES,
                    tuple(sorted(str(value) for value in geometry.geom_type.dropna().unique())),
                    provenance=provenance,
                ),
            )
        )
        if len(target) == 0 or geometry.dropna().empty:
            records.append(FactRecord.unknown(SPATIAL_BOUNDS, provenance=provenance))
        else:
            records.append(
                FactRecord.known(
                    SPATIAL_BOUNDS,
                    tuple(float(value) for value in target.total_bounds),
                    provenance=provenance,
                )
            )

        return DatasetSnapshot(
            subject=SubjectRef(
                id=f"memory:geodataframe:{id(target):x}",
                kind=SubjectKind.VECTOR,
                label="GeoDataFrame",
                adapter=self.name,
            ),
            facts=FactStore(records),
        )
