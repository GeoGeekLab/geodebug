# 03 — Same pixels, half a cell east

Two raster exports are stacked for a pixel-wise comparison. Both are UTM zone 54N, both have
10 m pixels, both are 32 × 32, and the arrays contain exactly the same values.

One export starts 5 m farther east.

That is half a pixel.

A NumPy subtraction happily reports a perfect match because it only sees array indexes.

## Run it

```bash
python make_case.py
python wrong.py
geodebug compare reference.tif candidate.tif
```

`wrong.py` reports the same CRS, shape, resolution, and a mean absolute pixel difference of
`0.0`.

GeoDebug reports:

```text
WARNING GEO404  Raster grids are not aligned to the same pixel lattice.
```

Before cell-by-cell math, put both rasters on the same target grid.

The fixture is centered on realistic UTM coordinates near central Tokyo and uses a 5 m origin
offset against a 10 m pixel size.

Background:
- https://rasterio.readthedocs.io/en/stable/api/rasterio.transform.html
