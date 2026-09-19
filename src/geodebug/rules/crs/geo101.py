from geodebug.facts.keys import CRS_PRESENT
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


class MissingCRSRule:
    spec = RuleSpec(
        id="GEO101",
        name="missing-crs",
        category="crs.definition",
        scope=RuleScope.DATASET,
        default_severity=Severity.WARNING,
        certainty=Certainty.DETERMINISTIC,
        requires=(CRS_PRESENT,),
        cost=CostClass.METADATA,
        fix_safety=FixSafety.REVIEW_REQUIRED,
    )

    def evaluate(self, context: EvaluationContext) -> RuleResult:
        subject = context.primary
        if subject is None:
            return RuleResult.not_applicable()

        fact = subject.facts.get(CRS_PRESENT)
        if fact is None or fact.state is FactState.UNKNOWN:
            return RuleResult.unknown("CRS presence could not be established.")
        if fact.state is FactState.NOT_APPLICABLE:
            return RuleResult.not_applicable()
        if bool(fact.value):
            return RuleResult.passed()

        return RuleResult(
            state=RuleState.FAIL,
            message="Dataset has no declared coordinate reference system.",
            evidence=(Evidence(key=CRS_PRESENT, value=False),),
            implication="Spatial coordinates cannot be interpreted reliably without a CRS.",
        )
