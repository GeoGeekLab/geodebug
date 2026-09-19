from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from geodebug.models.context import EvaluationContext
from geodebug.models.diagnostics import SuggestedAction
from geodebug.models.enums import Certainty, CostClass, FixSafety, RuleScope, RuleState, Severity
from geodebug.models.evidence import Evidence


@dataclass(frozen=True, slots=True)
class RuleSpec:
    id: str
    name: str
    category: str
    scope: RuleScope
    default_severity: Severity
    certainty: Certainty
    requires: tuple[str, ...] = ()
    cost: CostClass = CostClass.METADATA
    fix_safety: FixSafety = FixSafety.NONE


@dataclass(frozen=True, slots=True)
class RuleResult:
    state: RuleState
    message: str | None = None
    evidence: tuple[Evidence, ...] = ()
    implication: str | None = None
    suggestion: SuggestedAction | None = None

    @classmethod
    def passed(cls) -> RuleResult:
        return cls(state=RuleState.PASS)

    @classmethod
    def unknown(cls, message: str | None = None) -> RuleResult:
        return cls(state=RuleState.UNKNOWN, message=message)

    @classmethod
    def not_applicable(cls) -> RuleResult:
        return cls(state=RuleState.NOT_APPLICABLE)


class Rule(Protocol):
    spec: RuleSpec

    def evaluate(self, context: EvaluationContext) -> RuleResult: ...
