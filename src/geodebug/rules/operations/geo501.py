from geodebug.models.context import EvaluationContext
from geodebug.models.diagnostics import SuggestedAction
from geodebug.models.enums import (
    Certainty,
    CostClass,
    FixSafety,
    RuleScope,
    RuleState,
    Severity,
)
from geodebug.models.evidence import Evidence
from geodebug.rules.base import RuleResult, RuleSpec
from geodebug.rules.operations._geographic import geographic_crs_status


class AngularCRSBufferRule:
    spec = RuleSpec(
        id="GEO501",
        name="buffer-on-angular-crs",
        category="operation.measurement",
        scope=RuleScope.OPERATION,
        default_severity=Severity.ERROR,
        certainty=Certainty.DETERMINISTIC,
        requires=("crs.kind", "crs.axis_units", "operation.distance"),
        cost=CostClass.METADATA,
        fix_safety=FixSafety.REVIEW_REQUIRED,
    )

    def evaluate(self, context: EvaluationContext) -> RuleResult:
        operation = context.operation
        if operation is None or operation.name.casefold() != "buffer":
            return RuleResult.not_applicable()
        if "distance" not in operation.parameters:
            return RuleResult.unknown("Buffer distance was not provided.")

        state, evidence, message = geographic_crs_status(context)
        if state is RuleState.PASS:
            return RuleResult.passed()
        if state is RuleState.UNKNOWN:
            return RuleResult.unknown(message)

        distance = operation.parameters["distance"]
        return RuleResult(
            state=RuleState.FAIL,
            message="Buffer distance is interpreted in angular coordinate units.",
            evidence=(
                *evidence,
                Evidence(key="operation.distance", value=distance, origin="operation"),
            ),
            implication="The distance does not represent a metric buffer distance.",
            suggestion=SuggestedAction(
                action="project-before-buffer",
                safety=FixSafety.REVIEW_REQUIRED,
                detail=(
                    "Use a suitable projected CRS when the buffer distance "
                    "is intended to be linear."
                ),
            ),
        )
