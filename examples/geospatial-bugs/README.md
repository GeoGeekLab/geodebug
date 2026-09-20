# Geospatial bugs that still run

Five small reproductions of failures that show up in real geospatial pipelines.

No downloads. No remote APIs. No magic fixtures. Each case builds its own input data, runs code
that exits successfully, then shows what GeoDebug catches.

```bash
pip install "geodebug[all]"
```

| # | Case | The pipeline sees | GeoDebug |
| --- | --- | --- | --- |
| 01 | [500 m buffer in degrees](01-buffer-in-degrees/) | a polygon comes back | `GEO501` |
| 02 | [Web Mercator dumped into GeoJSON](02-web-mercator-as-geojson/) | valid JSON, valid Point | `GEO103` |
| 03 | [half-pixel raster shift](03-half-pixel-shift/) | same CRS, shape, resolution, values | `GEO404` |
| 04 | [wrong region partition](04-wrong-region-partition/) | valid files, empty spatial join | `GEO402` |
| 05 | [NoData/mask disagreement](05-nodata-mask-conflict/) | raster opens, both conventions work | `GEO304` |

Every `wrong.py` exits 0. That's the point.

Run any case from its directory:

```bash
python make_case.py
python wrong.py
```

Then run the GeoDebug command shown in that case's README.
