from collections.abc import Sequence

from geodebug.facts.keys import CRS_AXIS_UNITS, CRS_KIND
from geodebug.models.context import EvaluationContext
from geodebug.models.diagnostics import SuggestedAction
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


class AngularCRSBufferRule:
    spec = RuleSpec(
        id="GEO501",
        name="buffer-on-angular-crs",
        category="operation.measurement",
        scope=RuleScope.OPERATION,
        default_severity=Severity.ERROR,
        certainty=Certainty.DETERMINISTIC,
        requires=(CRS_KIND, CRS_AXIS_UNITS, "operation.distance"),
        cost=CostClass.METADATA,
        fix_safety=FixSafety.REVIEW_REQUIRED,
    )

    def evaluate(self, context: EvaluationContext) -> RuleResult:
        operation = context.operation
        if operation is None or operation.name.casefold() != "buffer":
            return RuleResult.not_applicable()

        subject = context.primary
        if subject is None:
            return RuleResult.unknown("Buffer input is unavailable.")

        crs_kind = subject.facts.get(CRS_KIND)
        axis_units = subject.facts.get(CRS_AXIS_UNITS)
        if crs_kind is None or crs_kind.state is not FactState.KNOWN:
            return RuleResult.unknown("CRS type could not be established.")
        if str(crs_kind.value).casefold() != "geographic":
            return RuleResult.passed()
        if axis_units is None or axis_units.state is not FactState.KNOWN:
            return RuleResult.unknown("CRS axis units could not be established.")
        if "distance" not in operation.parameters:
            return RuleResult.unknown("Buffer distance was not provided.")

        units_value = axis_units.value
        if isinstance(units_value, Sequence) and not isinstance(units_value, str):
            units = tuple(str(unit) for unit in units_value)
        else:
            units = (str(units_value),)

        distance = operation.parameters["distance"]
        return RuleResult(
            state=RuleState.FAIL,
            message="Buffer distance is interpreted in angular coordinate units.",
            evidence=(
                Evidence(key=CRS_KIND, value="geographic"),
                Evidence(key=CRS_AXIS_UNITS, value=units),
                Evidence(key="operation.distance", value=distance, origin="operation"),
            ),
            implication="The distance does not represent a metric buffer distance.",
            suggestion=SuggestedAction(
                action="project-before-buffer",
                safety=FixSafety.REVIEW_REQUIRED,
                detail="Use a suitable projected CRS when the buffer distance is intended to be linear.",
            ),
        )
