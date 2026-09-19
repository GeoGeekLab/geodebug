from __future__ import annotations

from pathlib import Path
from typing import Any

from geodebug.adapters.base import (
    AdapterDependencyError,
    AdapterError,
    InspectOptions,
    path_subject_id,
)
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


class PyogrioAdapter:
    name = "pyogrio"
    _suffixes = {".fgb", ".gpkg", ".shp"}

    def supports(self, target: Any) -> int:
        if not isinstance(target, (str, Path)):
            return 0
        return 80 if Path(target).suffix.casefold() in self._suffixes else 0

    def inspect(self, target: Any, options: InspectOptions) -> DatasetSnapshot:
        try:
            import pyogrio
        except ImportError as exc:
            raise AdapterDependencyError(
                "Pyogrio support requires 'pip install geodebug[vector]'"
            ) from exc

        path = Path(target)
        try:
            info = pyogrio.read_info(path)
        except Exception as exc:
            raise AdapterError(f"unable to inspect vector dataset: {path}") from exc

        provenance = FactProvenance(origin=self.name, method="read_info")
        records = list(
            build_crs_facts(info.get("crs"), origin=self.name, method="read_info.crs")
        )

        feature_count = info.get("features")
        if isinstance(feature_count, int) and feature_count >= 0:
            records.append(
                FactRecord.known(VECTOR_GEOMETRY_COUNT, feature_count, provenance=provenance)
            )
        else:
            records.append(FactRecord.unknown(VECTOR_GEOMETRY_COUNT, provenance=provenance))

        geometry_type = info.get("geometry_type")
        if geometry_type:
            records.append(
                FactRecord.known(
                    VECTOR_GEOMETRY_TYPES,
                    (str(geometry_type),),
                    provenance=provenance,
                )
            )
        else:
            records.append(FactRecord.unknown(VECTOR_GEOMETRY_TYPES, provenance=provenance))

        total_bounds = info.get("total_bounds")
        if total_bounds is not None and len(total_bounds) == 4:
            records.append(
                FactRecord.known(
                    SPATIAL_BOUNDS,
                    tuple(float(value) for value in total_bounds),
                    provenance=provenance,
                )
            )
        else:
            records.append(FactRecord.unknown(SPATIAL_BOUNDS, provenance=provenance))

        if options.deep:
            try:
                frame = pyogrio.read_dataframe(path)
                geometry = frame.geometry
                records.extend(
                    (
                        FactRecord.known(
                            VECTOR_INVALID_GEOMETRY_COUNT,
                            int((~geometry.is_valid & ~geometry.isna()).sum()),
                            provenance=FactProvenance(origin=self.name, method="read_dataframe"),
                        ),
                        FactRecord.known(
                            VECTOR_EMPTY_GEOMETRY_COUNT,
                            int(geometry.is_empty.sum()),
                            provenance=FactProvenance(origin=self.name, method="read_dataframe"),
                        ),
                    )
                )
            except Exception as exc:
                raise AdapterError(f"unable to scan vector geometries: {path}") from exc
        else:
            records.extend(
                (
                    FactRecord.unknown(VECTOR_INVALID_GEOMETRY_COUNT, provenance=provenance),
                    FactRecord.unknown(VECTOR_EMPTY_GEOMETRY_COUNT, provenance=provenance),
                )
            )

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
