from geodebug.facts.keys import RELATION_GRID_ALIGNED, RELATION_GRID_OFFSET_PIXELS
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


class RasterGridMisalignmentRule:
    spec = RuleSpec(
        id="GEO404",
        name="raster-grid-misalignment",
        category="relation.grid",
        scope=RuleScope.RELATION,
        default_severity=Severity.WARNING,
        certainty=Certainty.DETERMINISTIC,
        requires=(RELATION_GRID_ALIGNED,),
        cost=CostClass.METADATA,
        fix_safety=FixSafety.REVIEW_REQUIRED,
    )

    def evaluate(self, context: EvaluationContext) -> RuleResult:
        if len(context.subjects) != 2:
            return RuleResult.not_applicable()

        aligned = context.facts.get(RELATION_GRID_ALIGNED)
        if aligned is None or aligned.state is FactState.UNKNOWN:
            return RuleResult.unknown("Raster grid alignment could not be established.")
        if aligned.state is FactState.NOT_APPLICABLE:
            return RuleResult.not_applicable()
        if bool(aligned.value):
            return RuleResult.passed()

        evidence = [Evidence(key=RELATION_GRID_ALIGNED, value=False)]
        offset = context.facts.get(RELATION_GRID_OFFSET_PIXELS)
        if offset is not None and offset.state is FactState.KNOWN:
            evidence.append(Evidence(key=RELATION_GRID_OFFSET_PIXELS, value=offset.value))

        return RuleResult(
            state=RuleState.FAIL,
            message="Raster grids are not aligned to the same pixel lattice.",
            evidence=tuple(evidence),
            implication="Cell-by-cell operations may require an explicit resampling step.",
        )
