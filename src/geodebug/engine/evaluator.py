from geodebug.engine.fingerprint import diagnostic_fingerprint
from geodebug.engine.policy import Policy
from geodebug.engine.registry import RuleRegistry
from geodebug.models.context import EvaluationContext
from geodebug.models.enums import RuleState, Severity
from geodebug.models.report import (
    DiagnosticModel,
    EvidenceModel,
    Report,
    RunInfo,
    SubjectModel,
    SuggestedActionModel,
    SummaryModel,
    ToolInfo,
)
from geodebug.version import __version__


class Evaluator:
    def __init__(self, registry: RuleRegistry, *, policy: Policy | None = None) -> None:
        self._registry = registry
        self._policy = policy or Policy()

    def evaluate(self, context: EvaluationContext) -> Report:
        diagnostics: list[DiagnosticModel] = []
        passed_rules = 0
        unknown_rules = 0
        not_applicable_rules = 0

        subject_ids = tuple(subject.subject.id for subject in context.subjects)
        operation_name = context.operation.name if context.operation is not None else None

        for rule in self._registry.all():
            result = rule.evaluate(context)
            if result.state is RuleState.PASS:
                passed_rules += 1
                continue
            if result.state is RuleState.UNKNOWN:
                unknown_rules += 1
                continue
            if result.state is RuleState.NOT_APPLICABLE:
                not_applicable_rules += 1
                continue

            severity = self._policy.severity_for(rule.spec)
            fingerprint = diagnostic_fingerprint(
                rule_id=rule.spec.id,
                subject_ids=subject_ids,
                operation_name=operation_name,
                evidence=result.evidence,
            )
            diagnostics.append(
                DiagnosticModel(
                    fingerprint=fingerprint,
                    rule_id=rule.spec.id,
                    severity=severity,
                    certainty=rule.spec.certainty,
                    subject_ids=list(subject_ids),
                    message=result.message or rule.spec.name,
                    evidence=[
                        EvidenceModel(
                            key=item.key,
                            value=item.value,
                            origin=item.origin,
                            certainty=item.certainty,
                        )
                        for item in result.evidence
                    ],
                    implication=result.implication,
                    suggestion=(
                        SuggestedActionModel(
                            action=result.suggestion.action,
                            safety=result.suggestion.safety,
                            detail=result.suggestion.detail,
                        )
                        if result.suggestion is not None
                        else None
                    ),
                )
            )

        diagnostics.sort(
            key=lambda item: (_severity_rank(item.severity), item.rule_id, item.fingerprint)
        )
        summary = SummaryModel(
            errors=sum(item.severity is Severity.ERROR for item in diagnostics),
            warnings=sum(item.severity is Severity.WARNING for item in diagnostics),
            notes=sum(item.severity is Severity.NOTE for item in diagnostics),
            passed_rules=passed_rules,
            unknown_rules=unknown_rules,
            not_applicable_rules=not_applicable_rules,
        )
        return Report(
            tool=ToolInfo(version=__version__),
            run=RunInfo(profile=self._policy.profile),
            subjects=[
                SubjectModel(
                    id=item.subject.id,
                    kind=item.subject.kind,
                    uri=item.subject.uri,
                    label=item.subject.label,
                )
                for item in context.subjects
            ],
            diagnostics=diagnostics,
            summary=summary,
        )


def _severity_rank(severity: Severity) -> int:
    return {
        Severity.ERROR: 0,
        Severity.WARNING: 1,
        Severity.NOTE: 2,
    }[severity]
