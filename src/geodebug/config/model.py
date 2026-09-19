from __future__ import annotations

from datetime import date
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from geodebug.engine.policy import Policy, Suppression
from geodebug.models.enums import Severity


class ProfileName(StrEnum):
    DEFAULT = "default"
    STRICT = "strict"
    EXPLORATORY = "exploratory"


class FailOnName(StrEnum):
    ERROR = "error"
    WARNING = "warning"
    NONE = "none"


def _rule_id(value: str) -> str:
    normalized = value.upper()
    if len(normalized) != 6 or not normalized.startswith("GEO") or not normalized[3:].isdigit():
        raise ValueError("rule id must match GEO###")
    return normalized


class RulesConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    disable: list[str] = Field(default_factory=list)
    severity: dict[str, Severity] = Field(default_factory=dict)

    @field_validator("disable")
    @classmethod
    def validate_disabled_rules(cls, values: list[str]) -> list[str]:
        return [_rule_id(value) for value in values]

    @field_validator("severity")
    @classmethod
    def validate_severity_rules(cls, values: dict[str, Severity]) -> dict[str, Severity]:
        return {_rule_id(rule_id): severity for rule_id, severity in values.items()}


class SuppressionConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rule: str
    path: str = "*"
    reason: str = Field(min_length=1)
    expires: date | None = None

    @field_validator("rule")
    @classmethod
    def validate_rule(cls, value: str) -> str:
        return _rule_id(value)


class GeoDebugConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["1"] = "1"
    profile: ProfileName = ProfileName.DEFAULT
    fail_on: FailOnName = FailOnName.ERROR
    rules: RulesConfig = Field(default_factory=RulesConfig)
    suppress: list[SuppressionConfig] = Field(default_factory=list)

    def to_policy(
        self,
        *,
        profile: ProfileName | None = None,
        today: date | None = None,
    ) -> Policy:
        current_date = today or date.today()
        suppressions = tuple(
            Suppression(
                rule_id=item.rule,
                path_pattern=item.path,
                reason=item.reason,
            )
            for item in self.suppress
            if item.expires is None or item.expires >= current_date
        )
        return Policy(
            profile=(profile or self.profile).value,
            severity_overrides=self.rules.severity,
            disabled_rules=frozenset(self.rules.disable),
            suppressions=suppressions,
        )
