# 04 — The empty spatial join was the wrong partition

A batch job expects detections for Tokyo. The object-store key resolves to the Sapporo partition
instead.

Both files are valid GeoJSON. The schemas are right. The spatial join returns zero rows and the
job can continue with an empty result.

This is the kind of failure that often gets misread as "there were no detections today."

## Run it

```bash
python make_case.py
python wrong.py
geodebug compare aoi_tokyo.geojson detections_sapporo.geojson
```

`wrong.py` reports three input detections and zero joined rows.

GeoDebug reports:

```text
ERROR GEO402  Dataset extents do not overlap.
```

The fix is upstream: load the partition that belongs to the AOI. Reprojecting or buffering will
not make Tokyo overlap Sapporo.
