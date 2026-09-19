# GeoDebug

Deterministic diagnostics for geospatial data and workflows.

**Find the geographic bug, not just the code bug.**

GeoDebug is an early-stage GeoGeekLab project for turning geospatial correctness rules into explicit, testable diagnostics. The core is intentionally independent of GIS file formats and language models: adapters produce normalized facts, rules evaluate spatial invariants, and reporters expose stable diagnostics.

## Status

The repository is in kernel development. The current vertical slice includes the fact model, rule engine, canonical report schema, CLI rule inspection, and three sentinel rules:

- `GEO101` — missing CRS
- `GEO201` — invalid geometry
- `GEO501` — metric buffer on a geographic CRS

File-format adapters and user-facing `check` / `compare` workflows are the next milestone.

## Architecture

```text
adapter -> facts -> rules -> diagnostics -> report
```

Rules never read files directly and adapters never emit diagnostics.

## Development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'

ruff check .
mypy src/geodebug
pytest
```

Inspect the registered rules:

```bash
geodebug rules list
geodebug rules show GEO501
```

Print the canonical report JSON Schema:

```bash
geodebug schema
```

See [`docs/architecture.md`](docs/architecture.md) for the kernel contracts.
