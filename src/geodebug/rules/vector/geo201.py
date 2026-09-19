from geodebug.facts.keys import VECTOR_GEOMETRY_COUNT, VECTOR_INVALID_GEOMETRY_COUNT
from geodebug.models.context import EvaluationContext
from geodebug.models.enums import (
    Certainty,
    CostClass,
    FactState,
    FixSafety,
    RuleScope,
    RuleState,
    Severity,
    SubjectKind,
)
from geodebug.models.evidence import Evidence
from geodebug.rules.base import RuleResult, RuleSpec


class InvalidGeometryRule:
    spec = RuleSpec(
        id="GEO201",
        name="invalid-geometry",
        category="vector.geometry",
        scope=RuleScope.DATASET,
        default_severity=Severity.ERROR,
        certainty=Certainty.DETERMINISTIC,
        requires=(VECTOR_INVALID_GEOMETRY_COUNT,),
        cost=CostClass.FULL_SCAN,
        fix_safety=FixSafety.REVIEW_REQUIRED,
    )

    def evaluate(self, context: EvaluationContext) -> RuleResult:
        subject = context.primary
        if subject is None or subject.subject.kind is not SubjectKind.VECTOR:
            return RuleResult.not_applicable()

        invalid = subject.facts.get(VECTOR_INVALID_GEOMETRY_COUNT)
        if invalid is None or invalid.state is FactState.UNKNOWN:
            return RuleResult.unknown("Invalid geometry count is unavailable.")
        if invalid.state is FactState.NOT_APPLICABLE:
            return RuleResult.not_applicable()

        invalid_count = int(invalid.value)
        if invalid_count == 0:
            return RuleResult.passed()

        evidence = [Evidence(key=VECTOR_INVALID_GEOMETRY_COUNT, value=invalid_count)]
        count = subject.facts.get(VECTOR_GEOMETRY_COUNT)
        if count is not None and count.state is FactState.KNOWN:
            evidence.append(Evidence(key=VECTOR_GEOMETRY_COUNT, value=int(count.value)))

        return RuleResult(
            state=RuleState.FAIL,
            message="Dataset contains invalid geometries.",
            evidence=tuple(evidence),
            implication="Topological operations may fail or return misleading results.",
        )
