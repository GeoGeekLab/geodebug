# 01 — A 500 m road buffer in degrees

A road-closure feed arrives as GeoJSON around Tokyo Station. The downstream job needs a 500 m
impact zone.

The obvious line runs:

```python
buffers = roads.geometry.buffer(500)
```

GeoPandas warns because the data is geographic, but it still returns a polygon. In a batch job
where warnings are not fatal, the pipeline keeps moving.

## Run it

```bash
python make_case.py
python wrong.py
geodebug preflight road_segment.geojson --operation buffer --distance 500
```

`wrong.py` prints a buffer count and bounds. No exception is raised.

GeoDebug stops on:

```text
ERROR GEO501  Buffer distance is interpreted in angular coordinate units.
```

The input is RFC 7946 GeoJSON, so its coordinates are longitude/latitude in degrees. A raw
`buffer(500)` uses those coordinate units; it does not mean 500 meters.

Fix the workflow by projecting to an appropriate local projected CRS before the metric buffer.

Background:
- https://www.rfc-editor.org/rfc/rfc7946.html#section-4
- https://geopandas.org/en/stable/docs/reference/api/geopandas.GeoSeries.buffer.html
