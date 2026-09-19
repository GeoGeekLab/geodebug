from datetime import date

import pytest

from geodebug.config.loader import ConfigError, load_config
from geodebug.config.model import ProfileName
from geodebug.models.enums import Severity


def test_config_builds_policy_with_active_suppression(tmp_path) -> None:
    config_path = tmp_path / ".geodebug.toml"
    config_path.write_text(
        """
profile = "strict"
fail_on = "warning"

[rules]
disable = ["geo201"]

[rules.severity]
GEO101 = "note"

[[suppress]]
rule = "GEO103"
path = "*.geojson"
reason = "Known wrapped source"
expires = 2030-01-01
""".strip(),
        encoding="utf-8",
    )

    config = load_config(config_path)
    policy = config.to_policy(today=date(2026, 9, 19))

    assert config.profile is ProfileName.STRICT
    assert policy.disabled_rules == frozenset({"GEO201"})
    assert policy.severity_overrides["GEO101"] is Severity.NOTE
    assert len(policy.suppressions) == 1


def test_expired_suppression_is_not_loaded_into_policy(tmp_path) -> None:
    config_path = tmp_path / ".geodebug.toml"
    config_path.write_text(
        """
[[suppress]]
rule = "GEO101"
path = "*"
reason = "Temporary"
expires = 2020-01-01
""".strip(),
        encoding="utf-8",
    )

    policy = load_config(config_path).to_policy(today=date(2026, 9, 19))

    assert policy.suppressions == ()


def test_invalid_rule_id_is_rejected(tmp_path) -> None:
    config_path = tmp_path / ".geodebug.toml"
    config_path.write_text(
        """
[rules]
disable = ["BAD"]
""".strip(),
        encoding="utf-8",
    )

    with pytest.raises(ConfigError, match="GEO###"):
        load_config(config_path)
