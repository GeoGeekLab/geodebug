# GeoDebug

Deterministic diagnostics for geospatial data and workflows.

**Find the geographic bug, not just the code bug.**

GeoDebug turns geospatial correctness rules into explicit, testable diagnostics. Adapters
observe datasets, rules evaluate spatial invariants, and the canonical JSON report provides a
stable integration boundary for CLI, CI, and future agent tooling.

## Install

Core GeoJSON support:

```bash
pip install geodebug
```

Optional format support:

```bash
pip install "geodebug[vector]"     # GPKG, Shapefile, FlatGeobuf
pip install "geodebug[raster]"     # GeoTIFF, COG, VRT
pip install "geodebug[parquet]"    # GeoParquet
pip install "geodebug[geopandas]"  # in-memory GeoDataFrame
pip install "geodebug[all]"
```

## Usage

Inspect normalized facts without diagnostics:

```bash
geodebug inspect roads.geojson
```

Run dataset checks:

```bash
geodebug check roads.geojson
geodebug check roads.geojson --deep
```

Compare two datasets:

```bash
geodebug compare dem-a.tif dem-b.tif
```

Emit the canonical JSON report:

```bash
geodebug check roads.geojson --format json
```

The default path is metadata-first. Full vector geometry scans are opt-in with `--deep`.

## Built-in rules

The v0.1 usable core currently includes:

- `GEO101` — missing CRS
- `GEO201` — invalid geometry
- `GEO402` — no spatial overlap
- `GEO404` — raster grid misalignment
- `GEO501` — metric buffer on a geographic CRS

Inspect rule contracts with:

```bash
geodebug rules list
geodebug rules show GEO404
```

## Architecture

```text
adapter -> facts -> rules -> diagnostics -> report
```

Rules never read files directly and adapters never emit diagnostics. Unknown evidence remains
`UNKNOWN`; it is never silently treated as a pass.

See [`docs/architecture.md`](docs/architecture.md) for the kernel contracts.

## Development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev,all]'

ruff check .
mypy src/geodebug
pytest
```
