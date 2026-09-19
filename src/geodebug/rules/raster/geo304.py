from geodebug.facts.keys import RASTER_NODATA_COLLISION_BANDS
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


class NoDataMaskCollisionRule:
    spec = RuleSpec(
        id="GEO304",
        name="nodata-collides-with-valid-mask",
        category="raster.nodata",
        scope=RuleScope.DATASET,
        default_severity=Severity.WARNING,
        certainty=Certainty.DETERMINISTIC,
        requires=(RASTER_NODATA_COLLISION_BANDS,),
        cost=CostClass.FULL_SCAN,
        fix_safety=FixSafety.REVIEW_REQUIRED,
    )

    def evaluate(self, context: EvaluationContext) -> RuleResult:
        subject = context.primary
        if subject is None or subject.subject.kind is not SubjectKind.RASTER:
            return RuleResult.not_applicable()

        fact = subject.facts.get(RASTER_NODATA_COLLISION_BANDS)
        if fact is None or fact.state is FactState.UNKNOWN:
            return RuleResult.unknown("NoData and mask consistency was not scanned.")
        if fact.state is FactState.NOT_APPLICABLE:
            return RuleResult.not_applicable()

        bands = tuple(int(value) for value in fact.value)
        if not bands:
            return RuleResult.passed()

        return RuleResult(
            state=RuleState.FAIL,
            message="NoData-valued pixels are marked valid by the dataset mask.",
            evidence=(Evidence(key=RASTER_NODATA_COLLISION_BANDS, value=bands),),
            implication=(
                "NoData metadata and validity-mask semantics disagree for one or more bands."
            ),
        )
