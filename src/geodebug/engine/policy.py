from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from fnmatch import fnmatchcase
from types import MappingProxyType

from geodebug.models.context import EvaluationContext
from geodebug.models.enums import Severity
from geodebug.rules.base import RuleSpec


@dataclass(frozen=True, slots=True)
class Suppression:
    rule_id: str
    path_pattern: str
    reason: str

    def matches(self, rule_id: str, context: EvaluationContext) -> bool:
        if self.rule_id != rule_id:
            return False
        for snapshot in context.subjects:
            subject = snapshot.subject
            target = subject.uri or subject.id
            if fnmatchcase(target, self.path_pattern):
                return True
        return False


@dataclass(frozen=True, slots=True)
class Policy:
    profile: str = "default"
    severity_overrides: Mapping[str, Severity] = field(default_factory=dict)
    disabled_rules: frozenset[str] = frozenset()
    suppressions: tuple[Suppression, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "severity_overrides",
            MappingProxyType(dict(self.severity_overrides)),
        )

    def severity_for(self, spec: RuleSpec) -> Severity:
        override = self.severity_overrides.get(spec.id)
        if override is not None:
            return override

        severity = spec.default_severity
        if self.profile == "strict" and severity is Severity.WARNING:
            return Severity.ERROR
        if self.profile == "exploratory" and severity is Severity.WARNING:
            return Severity.NOTE
        return severity

    def enables(self, spec: RuleSpec) -> bool:
        return spec.id not in self.disabled_rules

    def suppresses(self, spec: RuleSpec, context: EvaluationContext) -> bool:
        return any(item.matches(spec.id, context) for item in self.suppressions)
