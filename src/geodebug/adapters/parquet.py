from __future__ import annotations

import json
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
    VECTOR_GEOMETRY_COUNT,
    VECTOR_GEOMETRY_TYPES,
    VECTOR_INVALID_GEOMETRY_COUNT,
)
from geodebug.models.enums import SubjectKind
from geodebug.models.facts import FactProvenance, FactRecord, FactStore
from geodebug.models.subjects import DatasetSnapshot, SubjectRef


class GeoParquetAdapter:
    name = "geoparquet"

    def supports(self, target: Any) -> int:
        if not isinstance(target, (str, Path)):
            return 0
        return 95 if Path(target).suffix.casefold() in {".parquet", ".geoparquet"} else 0

    def inspect(self, target: Any, options: InspectOptions) -> DatasetSnapshot:
        del options
        try:
            import pyarrow.parquet as pq
        except ImportError as exc:
            raise AdapterDependencyError(
                "GeoParquet support requires 'pip install geodebug[parquet]'"
            ) from exc

        path = Path(target)
        try:
            parquet = pq.ParquetFile(path)
            metadata = parquet.schema_arrow.metadata or {}
            raw_geo = metadata.get(b"geo")
            if raw_geo is None:
                raise AdapterError("Parquet file does not contain GeoParquet metadata")
            geo = json.loads(raw_geo.decode("utf-8"))
        except AdapterError:
            raise
        except Exception as exc:
            raise AdapterError(f"unable to inspect GeoParquet dataset: {path}") from exc

        primary = geo.get("primary_column")
        columns = geo.get("columns", {})
        if not isinstance(primary, str) or not isinstance(columns, dict) or primary not in columns:
            raise AdapterError(\n                "GeoParquet metadata does not define a valid primary geometry column"\n            )
        column = columns[primary]
        if not isinstance(column, dict):
            raise AdapterError("GeoParquet primary geometry metadata is invalid")

        provenance = FactProvenance(origin=self.name, method="parquet.metadata")
        if "crs" not in column:
            crs_value: Any = "OGC:CRS84"
        else:
            crs_value = column.get("crs")

        records = list(build_crs_facts(crs_value, origin=self.name, method="geo.crs"))
        records.append(
            FactRecord.known(
                VECTOR_GEOMETRY_COUNT,
                parquet.metadata.num_rows,
                provenance=provenance,
            )
        )
        geometry_types = column.get("geometry_types")
        if isinstance(geometry_types, list):
            records.append(
                FactRecord.known(
                    VECTOR_GEOMETRY_TYPES,
                    tuple(sorted(str(value) for value in geometry_types)),
                    provenance=provenance,
                )
            )
        else:
            records.append(FactRecord.unknown(VECTOR_GEOMETRY_TYPES, provenance=provenance))

        bbox = column.get("bbox")
        if isinstance(bbox, list) and len(bbox) >= 4:
            records.append(
                FactRecord.known(
                    SPATIAL_BOUNDS,
                    tuple(float(value) for value in bbox[:4]),
                    provenance=provenance,
                )
            )
        else:
            records.append(FactRecord.unknown(SPATIAL_BOUNDS, provenance=provenance))

        records.append(
            FactRecord.unknown(VECTOR_INVALID_GEOMETRY_COUNT, provenance=provenance)
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
