from geodebug.models.context import EvaluationContext
from geodebug.models.enums import (
    Certainty,
    CostClass,
    FixSafety,
    RuleScope,
    RuleState,
    Severity,
)
from geodebug.rules.base import RuleResult, RuleSpec
from geodebug.rules.operations._geographic import geographic_crs_status


class PlanarAreaOnGeographicCRSRule:
    spec = RuleSpec(
        id="GEO502",
        name="planar-area-on-geographic-crs",
        category="operation.measurement",
        scope=RuleScope.OPERATION,
        default_severity=Severity.ERROR,
        certainty=Certainty.DETERMINISTIC,
        requires=("crs.kind", "crs.axis_units"),
        cost=CostClass.METADATA,
        fix_safety=FixSafety.REVIEW_REQUIRED,
    )

    def evaluate(self, context: EvaluationContext) -> RuleResult:
        operation = context.operation
        if operation is None or operation.name.casefold() != "area":
            return RuleResult.not_applicable()

        state, evidence, message = geographic_crs_status(context)
        if state is RuleState.PASS:
            return RuleResult.passed()
        if state is RuleState.UNKNOWN:
            return RuleResult.unknown(message)

        return RuleResult(
            state=RuleState.FAIL,
            message="Planar area is being evaluated in a geographic CRS.",
            evidence=evidence,
            implication="The resulting area is expressed in angular-coordinate units, not square metres.",
        )
