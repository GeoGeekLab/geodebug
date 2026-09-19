from dataclasses import dataclass

from geodebug.models.enums import Certainty, FixSafety, Severity
from geodebug.models.evidence import Evidence


@dataclass(frozen=True, slots=True)
class SuggestedAction:
    action: str
    safety: FixSafety
    detail: str | None = None


@dataclass(frozen=True, slots=True)
class InternalDiagnostic:
    fingerprint: str
    rule_id: str
    severity: Severity
    certainty: Certainty
    subject_ids: tuple[str, ...]
    message: str
    evidence: tuple[Evidence, ...]
    implication: str | None = None
    suggestion: SuggestedAction | None = None
