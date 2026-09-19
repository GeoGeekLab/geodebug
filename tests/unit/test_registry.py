import pytest

from geodebug.engine.registry import DuplicateRuleError, RuleRegistry
from geodebug.rules.crs.geo101 import MissingCRSRule


def test_registry_rejects_duplicate_rule_ids() -> None:
    registry = RuleRegistry()
    registry.register(MissingCRSRule())

    with pytest.raises(DuplicateRuleError):
        registry.register(MissingCRSRule())
