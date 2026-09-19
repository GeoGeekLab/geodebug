# GeoDebug

Deterministic diagnostics for geospatial data and workflows.

**Find the geographic bug, not just the code bug.**

GeoDebug turns geospatial correctness rules into explicit, testable diagnostics. Adapters
observe datasets, rules evaluate spatial invariants, and the canonical JSON report provides a
stable integration boundary for CLI, CI, and future agent tooling.

## Install

PyPI publication is not enabled for 0.1.0. Install the tagged release directly
from GitHub:

```bash
pip install "geodebug @ git+https://github.com/GeoGeekLab/geodebug.git@v0.1.0"
```

Optional format support can be installed from the same tag:

```bash
pip install "geodebug[vector] @ git+https://github.com/GeoGeekLab/geodebug.git@v0.1.0"
pip install "geodebug[raster] @ git+https://github.com/GeoGeekLab/geodebug.git@v0.1.0"
pip install "geodebug[parquet] @ git+https://github.com/GeoGeekLab/geodebug.git@v0.1.0"
pip install "geodebug[geopandas] @ git+https://github.com/GeoGeekLab/geodebug.git@v0.1.0"
pip install "geodebug[all] @ git+https://github.com/GeoGeekLab/geodebug.git@v0.1.0"
```

## Usage

Inspect normalized facts without diagnostics:

```bash
geodebug inspect roads.geojson
```

Run dataset checks:

```bash
geodebug check roads.geojson
geodebug check landcover.tif --deep
```

Compare two datasets:

```bash
geodebug compare dem-a.tif dem-b.tif
```

Check an operation before execution:

```bash
geodebug preflight roads.geojson --operation buffer --distance 500
geodebug preflight parcels.geojson --operation area
```

Emit the canonical JSON report:

```bash
geodebug check roads.geojson --format json
```

The default path is metadata-first. Full geometry or raster scans are opt-in with `--deep`.

## Project policy

GeoDebug searches the current directory and its parents for `.geodebug.toml`. An explicit
config path can be supplied with `--config`.

```toml
schema_version = "1"
profile = "default"
fail_on = "error"

[rules]
disable = []

[rules.severity]
GEO101 = "error"

[[suppress]]
rule = "GEO103"
path = "legacy/*.geojson"
reason = "Known upstream coordinate convention"
expires = 2027-01-01
```

Profiles do not change rule truth values. `strict` promotes warnings to errors;
`exploratory` demotes warnings to notes. Explicit severity overrides take precedence.
Suppressions require a reason and may expire.

## Built-in rules

The current v0.1 rule set includes:

- `GEO101` — missing CRS
- `GEO103` — geographic coordinate out of range
- `GEO105` — projected data outside CRS area of use
- `GEO201` — invalid geometry
- `GEO301` — invalid or singular raster transform
- `GEO304` — NoData value conflicts with the validity mask
- `GEO402` — no spatial overlap
- `GEO404` — raster grid misalignment
- `GEO501` — metric buffer on a geographic CRS
- `GEO502` — planar area on a geographic CRS
- `GEO503` — planar distance or length on a geographic CRS

Inspect rule contracts with:

```bash
geodebug rules list
geodebug rules show GEO304
```

## Architecture

```text
adapter -> facts -> rules -> diagnostics -> report
```

Rules never read files directly and adapters never emit diagnostics. Unknown evidence remains
`UNKNOWN`; it is never silently treated as a pass.

See [`docs/architecture.md`](docs/architecture.md) for the kernel contracts and [`docs/rules.md`](docs/rules.md) for the released diagnostic contracts.

## Development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev,all]'

ruff check .
mypy src/geodebug
pytest
```

Golden rule cases live in `tests/golden/cases.toml`. Each case declares both expected
diagnostics and rules that must not be reported. The release gate also enforces
four-state rule contracts, metamorphic corrections, clean-corpus silence, and
installable wheel validation.
