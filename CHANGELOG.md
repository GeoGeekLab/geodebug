# Changelog

All notable changes to GeoDebug are documented here.

## 0.1.2 - 2026-09-20

### Added

- Add `geodebug demo` for a zero-setup GEO501 buffer failure.
- Add five runnable geospatial failure cases for CRS, grid alignment, dataset overlap,
  and NoData/mask semantics.
- Add a half-pixel raster shift visual for GEO404.

### Changed

- Exercise the failure cases in integration CI.
- Smoke-test `geodebug demo` from the built wheel before release.

## 0.1.1 - 2026-09-20

### Changed

- Publish releases to PyPI from GitHub Actions with Trusted Publishing.
- Rework the README front door around geospatial correctness and a failing buffer example.
- Tighten package metadata for PyPI search and discovery.
- Make `pip install geodebug` the default install path.

## 0.1.0 - 2026-09-19

### Added

- Deterministic fact, rule, diagnostic, and report kernel.
- GeoJSON, Pyogrio, Rasterio, GeoParquet, and GeoPandas adapters.
- Metadata-first `inspect`, `check`, and `compare` workflows.
- Operation-aware `preflight` checks.
- Project policy through `.geodebug.toml`, including profiles, rule overrides,
  disable lists, and reasoned suppressions.
- Canonical report schema `1.0.0` and config schema `1`.
- Eleven built-in high-signal rules across CRS, vector, raster, relations, and
  operation semantics.
- Golden false-positive contracts and cross-platform CI.
