from geodebug.engine.policy import Policy, Suppression
from geodebug.models.context import EvaluationContext
from geodebug.models.enums import (
    Certainty,
    FixSafety,
    RuleScope,
    Severity,
    SubjectKind,
)
from geodebug.models.facts import FactStore
from geodebug.models.subjects import DatasetSnapshot, SubjectRef
from geodebug.rules.base import RuleSpec


SPEC = RuleSpec(
    id="GEO999",
    name="test-rule",
    category="test",
    scope=RuleScope.DATASET,
    default_severity=Severity.WARNING,
    certainty=Certainty.DETERMINISTIC,
    fix_safety=FixSafety.NONE,
)


def _context(uri: str) -> EvaluationContext:
    return EvaluationContext(
        subjects=(
            DatasetSnapshot(
                subject=SubjectRef(
                    id="subject:test",
                    kind=SubjectKind.VECTOR,
                    uri=uri,
                    adapter="test",
                ),
                facts=FactStore(),
            ),
        )
    )


def test_strict_profile_promotes_warnings() -> None:
    assert Policy(profile="strict").severity_for(SPEC) is Severity.ERROR


def test_exploratory_profile_demotes_warnings() -> None:
    assert Policy(profile="exploratory").severity_for(SPEC) is Severity.NOTE


def test_explicit_override_wins_over_profile() -> None:
    policy = Policy(
        profile="strict",
        severity_overrides={"GEO999": Severity.NOTE},
    )

    assert policy.severity_for(SPEC) is Severity.NOTE


def test_path_suppression_matches_subject_uri() -> None:
    policy = Policy(
        suppressions=(
            Suppression(
                rule_id="GEO999",
                path_pattern="legacy/*.gpkg",
                reason="Known source issue",
            ),
        )
    )

    assert policy.suppresses(SPEC, _context("legacy/data.gpkg"))
    assert not policy.suppresses(SPEC, _context("clean/data.gpkg"))
