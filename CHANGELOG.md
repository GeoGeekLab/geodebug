# Changelog

All notable changes to GeoDebug are documented here.

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
