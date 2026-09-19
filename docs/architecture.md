# Kernel architecture

GeoDebug separates observation from diagnosis.

```text
raw source
   |
adapter
   |
DatasetSnapshot
   |
FactStore
   |
EvaluationContext
   |
RuleRegistry -> Rule.evaluate()
   |
RuleResult
   |
policy + fingerprinting
   |
Report
```

## Contracts

- Adapters observe sources and emit facts. They do not diagnose.
- Rules consume normalized facts. They do not perform I/O.
- `UNKNOWN` is distinct from `PASS`.
- Diagnostics carry evidence and a stable fingerprint.
- Rule IDs are stable public identifiers once released.
- The canonical JSON report is the integration boundary for CLI, CI, and future agent tooling.

## Sentinel rules

The kernel starts with three rules chosen to exercise different scopes:

- `GEO101`: dataset metadata semantics
- `GEO201`: vector geometry semantics
- `GEO501`: operation-aware measurement semantics

New rules should not be added until their PASS / FAIL / UNKNOWN / NOT_APPLICABLE boundaries are explicit in tests.
