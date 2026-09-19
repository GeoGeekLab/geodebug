# Contributing

Contributions should make GeoDebug more correct, more explicit, or easier to verify without
turning the project into a catalog of generic GIS advice.

## Principles

- Start from a concrete geospatial failure mode.
- Prefer deterministic evidence over model judgment.
- Keep adapters observational: adapters emit facts, not diagnostics.
- Keep rules pure: rules evaluate normalized facts and do not perform I/O.
- Preserve `UNKNOWN != PASS`.
- Avoid universal thresholds when the correct value depends on spatial context.
- Keep expensive scans explicit.
- Do not add automatic repair when the transformation can change scientific meaning.
- Keep public rule IDs, report schemas, and config schemas stable once released.

## Development

Requires Python 3.12 or newer.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev,all]'

ruff check .
mypy src/geodebug
pytest
```

Before opening a change:

1. run the focused tests for the behavior you changed,
2. run Ruff and strict Mypy,
3. run the relevant integration tests when an adapter or format changes,
4. inspect the complete diff,
5. update rule docs, schemas, or golden fixtures when the public contract changes.

## Adding a diagnostic rule

A rule should answer:

- What concrete spatial failure does it detect?
- What evidence makes the conclusion deterministic, inferred, or heuristic?
- When does it apply?
- When must it return `UNKNOWN`?
- When is it `NOT_APPLICABLE`?
- What false positive would be most damaging?

Every released rule must:

1. use a stable `GEOxxx` identifier,
2. document its scope, default severity, certainty, and semantics,
3. exercise `PASS`, `FAIL`, `UNKNOWN`, and `NOT_APPLICABLE`,
4. add or update golden cases when cross-rule behavior changes,
5. include `must_not_report` coverage where adjacent rules could cascade.

Do not create a rule merely because a GIS practice is common. Encode an invariant or a
well-bounded diagnostic condition.

## Adding or changing an adapter

Adapters normalize source-specific observations into GeoDebug facts.

They must not:

- choose diagnostic severity,
- emit `GEOxxx` findings,
- infer a missing CRS from plausible coordinates,
- silently trigger an expensive full scan in the metadata path.

When changing an adapter, include an integration fixture that exercises the real dependency when
practical.

## Changing public contracts

Treat these as versioned interfaces:

- released rule IDs and meanings,
- canonical report schema,
- project config schema,
- CLI exit behavior,
- documented Python API.

Compatibility changes require documentation and a versioning decision.

## Releases

Follow [docs/releasing.md](docs/releasing.md). Do not move published tags. A release must keep the
package version, changelog, schemas, built artifacts, and eventual `v<version>` tag consistent.
