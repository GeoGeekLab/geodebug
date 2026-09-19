from dataclasses import dataclass, field

from geodebug.models.enums import Severity
from geodebug.rules.base import RuleSpec


@dataclass(frozen=True, slots=True)
class Policy:
    profile: str = "default"
    severity_overrides: dict[str, Severity] = field(default_factory=dict)

    def severity_for(self, spec: RuleSpec) -> Severity:
        return self.severity_overrides.get(spec.id, spec.default_severity)
