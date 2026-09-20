# 05 — One pixel, two validity answers

An 8-bit raster keeps `nodata=0` from an upstream profile. A later export also writes a dataset
mask that marks every pixel as valid.

Now one zero-valued pixel has two answers:

```text
nodata metadata: invalid
dataset mask:    valid
```

Both conventions are legal on their own. Together they disagree about the analysis population.

## Run it

```bash
python make_case.py
python wrong.py
geodebug check surface_class.tif --deep
```

`wrong.py` counts valid pixels both ways. One path returns 15, the other 16.

GeoDebug reports:

```text
WARNING GEO304  NoData-valued pixels are marked valid by the dataset mask.
```

Decide which validity model is authoritative, then rewrite the raster metadata or mask so they
agree.

Rasterio documents this exact class of problem: valid-data masks and NoData values are separate
representations, and 8-bit data can contain legitimate zero values.

Background:
- https://rasterio.readthedocs.io/en/latest/topics/masks.html
