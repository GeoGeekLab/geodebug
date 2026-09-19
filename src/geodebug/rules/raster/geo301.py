from __future__ import annotations

import math

from geodebug.facts.keys import RASTER_TRANSFORM
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


class InvalidRasterTransformRule:
    spec = RuleSpec(
        id="GEO301",
        name="invalid-or-singular-transform",
        category="raster.grid",
        scope=RuleScope.DATASET,
        default_severity=Severity.ERROR,
        certainty=Certainty.DETERMINISTIC,
        requires=(RASTER_TRANSFORM,),
        cost=CostClass.METADATA,
        fix_safety=FixSafety.REVIEW_REQUIRED,
    )

    def evaluate(self, context: EvaluationContext) -> RuleResult:
        subject = context.primary
        if subject is None or subject.subject.kind is not SubjectKind.RASTER:
            return RuleResult.not_applicable()

        fact = subject.facts.get(RASTER_TRANSFORM)
        if fact is None or fact.state is FactState.UNKNOWN:
            return RuleResult.unknown("Raster transform could not be established.")
        if fact.state is FactState.NOT_APPLICABLE:
            return RuleResult.not_applicable()

        transform = _transform(fact.value)
        if transform is None:
            return RuleResult(
                state=RuleState.FAIL,
                message="Raster transform contains invalid coefficients.",
                evidence=(Evidence(key="raster.transform.issue", value="non-finite-or-malformed"),),
            )

        a, b, _, d, e, _ = transform
        determinant = a * e - b * d
        if not math.isclose(determinant, 0.0, abs_tol=1e-15):
            return RuleResult.passed()

        return RuleResult(
            state=RuleState.FAIL,
            message="Raster transform is singular.",
            evidence=(Evidence(key="raster.transform.determinant", value=determinant),),
            implication="Pixel coordinates cannot be mapped uniquely into spatial coordinates.",
        )


def _transform(value: object) -> tuple[float, float, float, float, float, float] | None:
    if not isinstance(value, (list, tuple)) or len(value) != 6:
        return None
    result: list[float] = []
    for item in value:
        if not isinstance(item, (int, float)) or not math.isfinite(item):
            return None
        result.append(float(item))
    return (result[0], result[1], result[2], result[3], result[4], result[5])
