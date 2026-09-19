# Security policy

## Reporting a vulnerability

Please report security issues privately through GitHub's security reporting features when
available. Do not publish exploit details in a public issue before a fix or mitigation is
available.

A useful report includes the affected file, adapter, workflow, or data format; concrete impact;
reproduction steps; required preconditions; and suggested mitigation if known.

## Scope

GeoDebug reads geospatial files and metadata through Python geospatial libraries and can perform
explicit deep scans. Security reports are especially relevant when crafted or untrusted input can:

- access files or paths outside the user-supplied target,
- cause unintended command execution,
- expose sensitive local data or configuration,
- trigger disproportionate CPU or memory consumption,
- bypass an explicit metadata-only or `--deep` boundary,
- corrupt or misrepresent the canonical diagnostic report,
- turn an unsafe operation into a misleadingly safe diagnostic result.

GeoDebug does not automatically repair datasets and does not execute arbitrary fixes from
diagnostic output.

## Dependency issues

If the issue originates in GDAL, PROJ, GEOS, Rasterio, Pyogrio, PyArrow, GeoPandas, Shapely, or
another dependency, report it upstream when appropriate. GeoDebug reports are still useful when
its own adapter or policy layer makes the upstream issue exploitable or materially worse.
