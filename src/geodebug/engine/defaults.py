from geodebug.engine.registry import RuleRegistry
from geodebug.rules.crs.geo101 import MissingCRSRule
from geodebug.rules.operations.geo501 import AngularCRSBufferRule
from geodebug.rules.vector.geo201 import InvalidGeometryRule


def build_default_registry() -> RuleRegistry:
    registry = RuleRegistry()
    registry.register(MissingCRSRule())
    registry.register(InvalidGeometryRule())
    registry.register(AngularCRSBufferRule())
    return registry
