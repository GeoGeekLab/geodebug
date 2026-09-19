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
    RASTER_BAND_COUNT,
    RASTER_DTYPES,
    RASTER_HEIGHT,
    RASTER_NODATA,
    RASTER_NODATA_COLLISION_BANDS,
    RASTER_RESOLUTION,
    RASTER_TRANSFORM,
    RASTER_WIDTH,
    SPATIAL_BOUNDS,
)
from geodebug.models.enums import FactState, SubjectKind
from geodebug.models.facts import FactProvenance, FactRecord, FactStore
from geodebug.models.subjects import DatasetSnapshot, SubjectRef


class RasterioAdapter:
    name = "rasterio"
    _suffixes = frozenset({".img", ".tif", ".tiff", ".vrt"})

    def supports(self, target: Any) -> int:
        if not isinstance(target, (str, Path)):
            return 0
        return 90 if Path(target).suffix.casefold() in self._suffixes else 0

    def inspect(self, target: Any, options: InspectOptions) -> DatasetSnapshot:
        try:
            import rasterio
        except ImportError as exc:
            raise AdapterDependencyError(
                "Raster support requires 'pip install geodebug[raster]'"
            ) from exc

        path = Path(target)
        try:
            with rasterio.open(path) as dataset:
                provenance = FactProvenance(origin=self.name, method="dataset.metadata")
                records = list(
                    build_crs_facts(
                        dataset.crs.to_wkt() if dataset.crs is not None else None,
                        origin=self.name,
                        method="dataset.crs",
                    )
                )
                records.extend(
                    (
                        FactRecord.known(
                            SPATIAL_BOUNDS,
                            tuple(float(value) for value in dataset.bounds),
                            provenance=provenance,
                        ),
                        FactRecord.known(RASTER_WIDTH, dataset.width, provenance=provenance),
                        FactRecord.known(RASTER_HEIGHT, dataset.height, provenance=provenance),
                        FactRecord.known(
                            RASTER_RESOLUTION,
                            (float(abs(dataset.res[0])), float(abs(dataset.res[1]))),
                            provenance=provenance,
                        ),
                        FactRecord.known(
                            RASTER_TRANSFORM,
                            (
                                float(dataset.transform.a),
                                float(dataset.transform.b),
                                float(dataset.transform.c),
                                float(dataset.transform.d),
                                float(dataset.transform.e),
                                float(dataset.transform.f),
                            ),
                            provenance=provenance,
                        ),
                        FactRecord.known(
                            RASTER_BAND_COUNT,
                            dataset.count,
                            provenance=provenance,
                        ),
                        FactRecord.known(
                            RASTER_DTYPES,
                            tuple(str(value) for value in dataset.dtypes),
                            provenance=provenance,
                        ),
                        FactRecord.known(
                            RASTER_NODATA,
                            dataset.nodata,
                            provenance=provenance,
                        ),
                    )
                )
                records.append(
                    _nodata_collision_fact(
                        dataset,
                        deep=options.deep,
                        provenance=provenance,
                    )
                )
        except Exception as exc:
            raise AdapterError(f"unable to inspect raster dataset: {path}") from exc

        return DatasetSnapshot(
            subject=SubjectRef(
                id=path_subject_id(path),
                kind=SubjectKind.RASTER,
                uri=path.as_posix(),
                label=path.name,
                adapter=self.name,
            ),
            facts=FactStore(records),
        )


def _nodata_collision_fact(
    dataset: Any,
    *,
    deep: bool,
    provenance: FactProvenance,
) -> FactRecord:
    nodata = dataset.nodata
    if nodata is None:
        return FactRecord(
            key=RASTER_NODATA_COLLISION_BANDS,
            state=FactState.NOT_APPLICABLE,
            provenance=provenance,
        )
    if not deep:
        return FactRecord.unknown(
            RASTER_NODATA_COLLISION_BANDS,
            provenance=provenance,
        )

    collisions: list[int] = []
    for band_index in range(1, dataset.count + 1):
        found = False
        for _, window in dataset.block_windows(band_index):
            values = dataset.read(band_index, window=window)
            valid_mask = dataset.dataset_mask(window=window) != 0
            nodata_values = values != values if nodata != nodata else values == nodata
            if (nodata_values & valid_mask).any():
                found = True
                break
        if found:
            collisions.append(band_index)

    return FactRecord.known(
        RASTER_NODATA_COLLISION_BANDS,
        tuple(collisions),
        provenance=FactProvenance(origin="rasterio", method="deep.nodata-mask-scan"),
    )
