# Architecture

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
- Policy can change presentation severity or suppress a finding, but it never
  changes a rule truth value.
- Diagnostics carry evidence and a stable fingerprint.
- Released rule IDs are stable public identifiers.
- The canonical JSON report is the integration boundary for CLI, CI, and agent tooling.
- Report schema `1.0.0` and config schema `1` are independently versioned
  from the Python package.

## Rule scopes

Dataset rules evaluate each subject independently. Relation rules evaluate a
multi-subject context. Operation rules require an explicit operation context.

A new rule is not release-ready until its `PASS`, `FAIL`, `UNKNOWN`, and
`NOT_APPLICABLE` states are exercised by the contract suite.

## Cost model

Metadata rules may run during ordinary checks. Full-scan rules require explicit
deep inspection. GeoDebug does not silently turn an expensive scan into a
default operation.
