from geodebug.facts.keys import RELATION_BOUNDS_OVERLAP, RELATION_OVERLAP_RATIO
from geodebug.models.context import EvaluationContext
from geodebug.models.enums import (
    Certainty,
    CostClass,
    FactState,
    FixSafety,
    RuleScope,
    RuleState,
    Severity,
)
from geodebug.models.evidence import Evidence
from geodebug.rules.base import RuleResult, RuleSpec


class NoSpatialOverlapRule:
    spec = RuleSpec(
        id="GEO402",
        name="no-spatial-overlap",
        category="relation.extent",
        scope=RuleScope.RELATION,
        default_severity=Severity.ERROR,
        certainty=Certainty.DETERMINISTIC,
        requires=(RELATION_BOUNDS_OVERLAP,),
        cost=CostClass.METADATA,
        fix_safety=FixSafety.NONE,
    )

    def evaluate(self, context: EvaluationContext) -> RuleResult:
        if len(context.subjects) != 2:
            return RuleResult.not_applicable()

        overlap = context.facts.get(RELATION_BOUNDS_OVERLAP)
        if overlap is None or overlap.state is FactState.UNKNOWN:
            return RuleResult.unknown("Dataset extent overlap could not be established.")
        if overlap.state is FactState.NOT_APPLICABLE:
            return RuleResult.not_applicable()
        if bool(overlap.value):
            return RuleResult.passed()

        evidence = [Evidence(key=RELATION_BOUNDS_OVERLAP, value=False)]
        ratio = context.facts.get(RELATION_OVERLAP_RATIO)
        if ratio is not None and ratio.state is FactState.KNOWN:
            evidence.append(Evidence(key=RELATION_OVERLAP_RATIO, value=float(ratio.value)))

        return RuleResult(
            state=RuleState.FAIL,
            message="Dataset extents do not overlap.",
            evidence=tuple(evidence),
            implication="Spatial operations between these datasets cannot produce intersecting results.",
        )
