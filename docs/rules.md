# Diagnostic rules

GeoDebug 0.1.0 ships eleven built-in rules. Rule IDs are stable public identifiers.

| Rule | Scope | Default | Description |
| --- | --- | --- | --- |
| [GEO101](rules/GEO101.md) | dataset | warning | Missing CRS |
| [GEO103](rules/GEO103.md) | dataset | error | Geographic coordinate out of range |
| [GEO105](rules/GEO105.md) | dataset | warning | Projected data outside CRS area of use |
| [GEO201](rules/GEO201.md) | dataset | error | Invalid geometry |
| [GEO301](rules/GEO301.md) | dataset | error | Invalid or singular raster transform |
| [GEO304](rules/GEO304.md) | dataset | warning | NoData value conflicts with valid mask |
| [GEO402](rules/GEO402.md) | relation | error | No spatial overlap |
| [GEO404](rules/GEO404.md) | relation | warning | Raster grid misalignment |
| [GEO501](rules/GEO501.md) | operation | error | Buffer on angular CRS |
| [GEO502](rules/GEO502.md) | operation | error | Planar area on geographic CRS |
| [GEO503](rules/GEO503.md) | operation | error | Planar distance on geographic CRS |
