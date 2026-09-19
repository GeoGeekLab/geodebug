## Summary

Describe the geospatial failure mode or repository problem and the smallest coherent change that
addresses it.

## Contract

- Behavior changed:
- Behavior intentionally unchanged:
- Compatibility or schema impact:

## Verification

List commands, fixtures, or checks actually run and their outcomes.

For diagnostic-rule changes, include the relevant `PASS / FAIL / UNKNOWN / NOT_APPLICABLE`
coverage and any `must_not_report` cases.

## Risk

Describe remaining correctness, geospatial-semantic, security, compatibility, performance, or
operational risk.

## Scope check

- [ ] The change has one coherent purpose.
- [ ] Unrelated cleanup is excluded.
- [ ] Tests or integration fixtures cover changed behavior where practical.
- [ ] Public rule, schema, CLI, or Python API documentation is updated when its contract changes.
- [ ] Expensive scans remain explicit rather than becoming an accidental default.
