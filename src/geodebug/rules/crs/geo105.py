from __future__ import annotations

import math
from typing import cast

from geodebug.facts.keys import (
    CRS_AREA_OF_USE_BOUNDS,
    CRS_AREA_OF_USE_NAME,
    CRS_KIND,
    CRS_WKT,
    SPATIAL_BOUNDS,
)
from geodebug.facts.spatial import geographic_bounds_overlap, transform_bounds
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
from geodebug.models.facts import FactRecord
from geodebug.rules.base import RuleResult, RuleSpec


class CRSAreaOfUseRule:
    spec = RuleSpec(
        id="GEO105",
        name="outside-crs-area-of-use",
        category="crs.area_of_use",
        scope=RuleScope.DATASET,
        default_severity=Severity.WARNING,
        certainty=Certainty.DETERMINISTIC,
        requires=(CRS_KIND, CRS_WKT, CRS_AREA_OF_USE_BOUNDS, SPATIAL_BOUNDS),
        cost=CostClass.METADATA,
        fix_safety=FixSafety.REVIEW_REQUIRED,
    )

    def evaluate(self, context: EvaluationContext) -> RuleResult:
        subject = context.primary
        if subject is None:
            return RuleResult.not_applicable()

        kind = _known(subject.facts.get(CRS_KIND))
        if kind is None:
            return RuleResult.unknown("CRS type could not be established.")
        if str(kind).casefold() != "projected":
            return RuleResult.not_applicable()

        wkt = _known(subject.facts.get(CRS_WKT))
        area = _bounds(_known(subject.facts.get(CRS_AREA_OF_USE_BOUNDS)))
        observed = _bounds(_known(subject.facts.get(SPATIAL_BOUNDS)))
        if not isinstance(wkt, str) or area is None or observed is None:
            return RuleResult.unknown("CRS area-of-use comparison could not be established.")

        geographic = transform_bounds(observed, wkt)
        if geographic is None:
            return RuleResult.unknown(
                "Dataset bounds could not be transformed to geographic coordinates."
            )
        if geographic_bounds_overlap(geographic, area):
            return RuleResult.passed()

        evidence = [
            Evidence(key="spatial.bounds.geographic", value=geographic),
            Evidence(key=CRS_AREA_OF_USE_BOUNDS, value=area),
        ]
        area_name = _known(subject.facts.get(CRS_AREA_OF_USE_NAME))
        if isinstance(area_name, str):
            evidence.append(Evidence(key=CRS_AREA_OF_USE_NAME, value=area_name))

        return RuleResult(
            state=RuleState.FAIL,
            message="Dataset lies outside the declared CRS area of use.",
            evidence=tuple(evidence),
            implication=(
                "The CRS may be inappropriate for this dataset or the CRS metadata "
                "may be incorrect."
            ),
        )


def _known(fact: FactRecord | None) -> object | None:
    if fact is None or fact.state is not FactState.KNOWN:
        return None
    return cast(object, fact.value)


def _bounds(value: object) -> tuple[float, float, float, float] | None:
    if not isinstance(value, (list, tuple)) or len(value) != 4:
        return None
    result: list[float] = []
    for item in value:
        if not isinstance(item, (int, float)) or not math.isfinite(item):
            return None
        result.append(float(item))
    return (result[0], result[1], result[2], result[3])
