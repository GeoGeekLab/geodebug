from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from geodebug.models.enums import Certainty, FixSafety, Severity, SubjectKind


class ToolInfo(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: Literal["geodebug"] = "geodebug"
    version: str


class RunInfo(BaseModel):
    model_config = ConfigDict(extra="forbid")

    profile: str = "default"


class SubjectModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    kind: SubjectKind
    uri: str | None = None
    label: str | None = None


class EvidenceModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    key: str
    value: Any
    origin: str | None = None
    certainty: Certainty


class SuggestedActionModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    action: str
    safety: FixSafety
    detail: str | None = None


class DiagnosticModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    fingerprint: str
    rule_id: str
    severity: Severity
    certainty: Certainty
    subject_ids: list[str]
    message: str
    evidence: list[EvidenceModel] = Field(default_factory=list)
    implication: str | None = None
    suggestion: SuggestedActionModel | None = None


class SummaryModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    errors: int = 0
    warnings: int = 0
    notes: int = 0
    passed_rules: int = 0
    unknown_rules: int = 0
    not_applicable_rules: int = 0


class Report(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["1.0.0"] = "1.0.0"
    tool: ToolInfo
    run: RunInfo = Field(default_factory=RunInfo)
    subjects: list[SubjectModel] = Field(default_factory=list)
    diagnostics: list[DiagnosticModel] = Field(default_factory=list)
    summary: SummaryModel = Field(default_factory=SummaryModel)
