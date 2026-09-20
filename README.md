<div align="center">

# GeoDebug

**Find the geographic bug, not just the code bug.**

Geospatial correctness checks for data and workflows.

[![CI](https://github.com/GeoGeekLab/geodebug/actions/workflows/ci.yml/badge.svg)](https://github.com/GeoGeekLab/geodebug/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/GeoGeekLab/geodebug?display_name=tag&sort=semver&style=flat-square)](https://github.com/GeoGeekLab/geodebug/releases/latest)
[![License: MIT](https://img.shields.io/badge/license-MIT-2ea44f?style=flat-square)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.12%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Typed](https://img.shields.io/badge/typing-strict-2F81F7?style=flat-square)](pyproject.toml)

[Architecture](docs/architecture.md) · [Rule catalog](docs/rules.md) · [Failure cases](examples/geospatial-bugs/) · [Contributing](CONTRIBUTING.md) · [Security](SECURITY.md) · [Changelog](CHANGELOG.md) · [Releases](https://github.com/GeoGeekLab/geodebug/releases)

</div>

---

Your file opens. Your geometry is valid. Your tests pass.

**Your result can still be geographically wrong.**

```text
✓ file readable
✓ geometry valid
✓ pipeline completed
✓ tests passed
? geographically correct
```

GeoDebug checks the last question. It catches spatial-semantic failures that ordinary software
tests and file validators can miss: CRS misuse, impossible coordinates, raster-grid
misalignment, cross-dataset incompatibility, NoData/mask conflicts, and operations whose units
do not mean what the code assumes.

## See the gap

This workflow can run without raising a Python exception:

```python
roads = gpd.read_file("roads.geojson")
buffered = roads.buffer(500)
buffered.to_file("roads_buffer.geojson")
```

But if the data uses a geographic CRS, `500` is interpreted in angular coordinate units rather
than meters.

GeoDebug makes that failure explicit before the operation becomes a result:

```console
$ geodebug preflight roads.geojson --operation buffer --distance 500

roads.geojson
ERROR GEO501  Buffer distance is interpreted in angular coordinate units.
  crs.kind: geographic
  crs.axis_units: degree, degree
  operation.distance: 500
1 error(s) · 0 warning(s) · 0 note(s) · 1 unknown
```

**The code can be valid while the geography is not.**

Install:

```bash
pip install geodebug
```

Then check a dataset or preflight an operation:

```bash
geodebug check roads.geojson
geodebug preflight roads.geojson --operation buffer --distance 500
```

## Where GeoDebug fits

| Layer | Question |
| --- | --- |
| Parser / schema | Can the data be read and interpreted structurally? |
| Geometry validity | Is the geometry structurally valid? |
| Software tests | Does the program behave as specified? |
| **GeoDebug** | **Does the data or operation make geographic sense?** |

GeoDebug does not replace GDAL, GeoPandas, Shapely, Rasterio, or PyProj. It turns spatial facts
exposed by the geospatial stack into a systematic, deterministic **geospatial correctness**
layer with stable diagnostics that can run locally or in CI.

No LLM in the core. No silent CRS guessing. No automatic "fix everything."

<p align="center">
  <img src="assets/geodebug-overview.svg" alt="GeoDebug architecture, diagnostic scopes, rule families, and CLI example" width="100%">
</p>

## What it catches

GeoDebug is built for bugs that ordinary syntax checks and file validators often miss.

| Domain | Examples |
| --- | --- |
| **CRS** | missing CRS, impossible angular coordinates, data outside a projected CRS area of use |
| **Vector** | invalid geometry |
| **Raster** | singular affine transforms, NoData/mask conflicts |
| **Relations** | non-overlapping datasets, half-pixel raster grid shifts |
| **Operations** | metric buffer, planar area, or planar distance on a geographic CRS |

A file can be valid in isolation and still be wrong **for the operation you are about to run**.
That distinction is the point.

## Failure cases

Want the bugs, not the architecture?

[Run five small failures that still produce valid-looking pipeline output.](examples/geospatial-bugs/)

<p align="center">
  <a href="examples/geospatial-bugs/03-half-pixel-shift/">
    <img src="assets/half-pixel-shift.svg" alt="Two 10 meter rasters with identical values but a five meter half-pixel grid offset" width="100%">
  </a>
</p>

Each case builds its own local fixture, runs the bad workflow, and is exercised in CI.

## Mental model

```text
source
  │
  ▼
adapter ──► facts ──► rules ──► diagnostics ──► report
                        ▲
                        │
              dataset / relation / operation
```

Three questions drive the engine:

1. **Dataset** — is this dataset internally spatially plausible?
2. **Relation** — are these datasets compatible with each other?
3. **Operation** — is this operation semantically valid for these coordinates and units?

Adapters observe. Rules diagnose. Policy decides what fails the build.

## CLI

| Command | Purpose |
| --- | --- |
| `geodebug inspect DATA` | Show normalized spatial facts without diagnosing |
| `geodebug check DATA` | Run dataset diagnostics |
| `geodebug compare A B` | Run dataset + relational diagnostics |
| `geodebug preflight DATA --operation ...` | Check operation semantics before execution |
| `geodebug rules list` | Inspect the built-in rule corpus |
| `geodebug schema` | Print the canonical report schema |

Full geometry or raster scans are opt-in:

```bash
geodebug check landcover.tif --deep
```

Machine-readable output is first-class:

```bash
geodebug check roads.geojson --format json
```

## Install

```bash
pip install geodebug
```

Need every adapter:

```bash
pip install "geodebug[all]"
```

Optional extras keep the core small:

| Extra | Support |
| --- | --- |
| core | GeoJSON |
| `vector` | GeoPackage, Shapefile, FlatGeobuf |
| `raster` | GeoTIFF, COG, VRT |
| `parquet` | GeoParquet |
| `geopandas` | in-memory GeoDataFrame |
| `all` | all optional adapters |

Requires Python **3.12+**.

## Diagnostic corpus

GeoDebug ships 11 built-in rules with stable IDs.

| Family | Rules |
| --- | --- |
| CRS | [`GEO101`](docs/rules/GEO101.md) missing CRS · [`GEO103`](docs/rules/GEO103.md) coordinate range · [`GEO105`](docs/rules/GEO105.md) area of use |
| Vector | [`GEO201`](docs/rules/GEO201.md) invalid geometry |
| Raster | [`GEO301`](docs/rules/GEO301.md) affine transform · [`GEO304`](docs/rules/GEO304.md) NoData/mask conflict |
| Relations | [`GEO402`](docs/rules/GEO402.md) spatial overlap · [`GEO404`](docs/rules/GEO404.md) grid alignment |
| Operations | [`GEO501`](docs/rules/GEO501.md) buffer · [`GEO502`](docs/rules/GEO502.md) area · [`GEO503`](docs/rules/GEO503.md) distance/length |

Every released rule has an explicit contract for `PASS`, `FAIL`, `UNKNOWN`, and
`NOT_APPLICABLE`.

```bash
geodebug rules show GEO404
```

## Project policy

Projects can tune severity, disable rules, and suppress known exceptions without changing rule
truth values.

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

GeoDebug searches the current directory and its parents for `.geodebug.toml`. Use `--config`
to select one explicitly.

Profiles are intentionally simple:

- `default` — rule defaults
- `strict` — warnings become errors
- `exploratory` — warnings become notes

Explicit overrides win. Suppressions require a reason and may expire.

## Contracts over vibes

A few things GeoDebug refuses to blur:

- **Adapters do not diagnose.** They normalize observations into facts.
- **Rules do not perform I/O.** They evaluate spatial invariants.
- **`UNKNOWN` is not `PASS`.** Missing evidence stays missing.
- **Policy does not rewrite truth.** It changes severity or visibility, not the rule result.
- **Expensive scans are explicit.** `--deep` means `--deep`.
- **Automatic repair is conservative.** A geometrically valid output is not necessarily a
  scientifically valid fix.

The canonical report schema is versioned independently at `1.0.0`; project config uses schema
version `1`.

```bash
geodebug schema
geodebug schema --kind config
```

## Development

```bash
git clone https://github.com/GeoGeekLab/geodebug.git
cd geodebug

python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev,all]'

ruff check .
mypy src/geodebug
pytest
```

The release gate checks more than unit tests: four-state rule contracts, golden
`must_not_report` cases, metamorphic corrections, clean-corpus silence, cross-platform smoke
tests, and installation from a freshly built wheel.

See [Architecture](docs/architecture.md), [Diagnostic rules](docs/rules.md), and
[Releasing](docs/releasing.md) for the internals.

## Contributing

Contributions should start from a concrete geospatial failure mode or a concrete
engineering improvement. New diagnostics must preserve the four-state rule contract and include
false-positive coverage where adjacent rules can cascade.

See [CONTRIBUTING.md](CONTRIBUTING.md).

## Security

Please report vulnerabilities privately through GitHub's security reporting features when
available. Do not publish exploit details in a public issue before a fix or mitigation is
available.

See [SECURITY.md](SECURITY.md).

## License

[MIT](LICENSE)

---

<div align="center">

**Geo to see. Geek to build.**

GeoGeekLab

</div>
