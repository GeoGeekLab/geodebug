from __future__ import annotations

import math

from geodebug.facts.keys import CRS_KIND, SPATIAL_BOUNDS
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


class GeographicCoordinateRangeRule:
    spec = RuleSpec(
        id="GEO103",
        name="geographic-coordinate-out-of-range",
        category="crs.coordinates",
        scope=RuleScope.DATASET,
        default_severity=Severity.ERROR,
        certainty=Certainty.DETERMINISTIC,
        requires=(CRS_KIND, SPATIAL_BOUNDS),
        cost=CostClass.METADATA,
        fix_safety=FixSafety.REVIEW_REQUIRED,
    )

    def evaluate(self, context: EvaluationContext) -> RuleResult:
        subject = context.primary
        if subject is None:
            return RuleResult.not_applicable()

        kind = subject.facts.get(CRS_KIND)
        if kind is None or kind.state is FactState.UNKNOWN:
            return RuleResult.unknown("CRS type could not be established.")
        if kind.state is FactState.NOT_APPLICABLE:
            return RuleResult.not_applicable()
        if str(kind.value).casefold() != "geographic":
            return RuleResult.not_applicable()

        bounds_fact = subject.facts.get(SPATIAL_BOUNDS)
        if bounds_fact is None or bounds_fact.state is FactState.UNKNOWN:
            return RuleResult.unknown("Dataset bounds could not be established.")
        if bounds_fact.state is FactState.NOT_APPLICABLE:
            return RuleResult.not_applicable()

        bounds = _bounds(bounds_fact.value)
        if bounds is None:
            return RuleResult.unknown("Dataset bounds are not finite numeric values.")

        xmin, ymin, xmax, ymax = bounds
        if ymin >= -90.0 and ymax <= 90.0 and xmin >= -360.0 and xmax <= 360.0:
            return RuleResult.passed()

        return RuleResult(
            state=RuleState.FAIL,
            message="Geographic coordinates exceed plausible angular ranges.",
            evidence=(Evidence(key=SPATIAL_BOUNDS, value=bounds),),
            implication=(
                "The declared geographic CRS is inconsistent with the observed coordinate range."
            ),
        )


def _bounds(value: object) -> tuple[float, float, float, float] | None:
    if not isinstance(value, (list, tuple)) or len(value) != 4:
        return None
    numbers: list[float] = []
    for item in value:
        if not isinstance(item, (int, float)) or not math.isfinite(item):
            return None
        numbers.append(float(item))
    return (numbers[0], numbers[1], numbers[2], numbers[3])
