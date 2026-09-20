# 02 — Web Mercator coordinates dumped into GeoJSON

A PostGIS or tile-service workflow stores a point in EPSG:3857. Someone serializes the raw
`x/y` values into GeoJSON without transforming them first.

The file is valid JSON. The geometry is a valid Shapely Point. The numbers are still wrong for
GeoJSON.

This case uses the Web Mercator coordinates of Tokyo Station:

```text
x = 15558802.40
y =  4256843.19
```

Those are meter-like projected coordinates, not longitude/latitude degrees.

## Run it

```bash
python make_case.py
python wrong.py
geodebug check station.geojson
```

`wrong.py` reports:

```text
geometry_type=Point
geometry_valid=True
```

GeoDebug reports:

```text
ERROR GEO103  Geographic coordinates exceed plausible angular ranges.
```

RFC 7946 GeoJSON uses WGS 84 longitude/latitude coordinates. Reproject before serializing the
geometry as GeoJSON.

Background:
- https://www.rfc-editor.org/rfc/rfc7946.html#section-4
