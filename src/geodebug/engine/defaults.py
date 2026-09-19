from geodebug.engine.registry import RuleRegistry
from geodebug.rules.crs.geo101 import MissingCRSRule
from geodebug.rules.operations.geo501 import AngularCRSBufferRule
from geodebug.rules.relations.geo402 import NoSpatialOverlapRule
from geodebug.rules.relations.geo404 import RasterGridMisalignmentRule
from geodebug.rules.vector.geo201 import InvalidGeometryRule


def build_default_registry() -> RuleRegistry:
    registry = RuleRegistry()
    registry.register(MissingCRSRule())
    registry.register(InvalidGeometryRule())
    registry.register(NoSpatialOverlapRule())
    registry.register(RasterGridMisalignmentRule())
    registry.register(AngularCRSBufferRule())
    return registry
