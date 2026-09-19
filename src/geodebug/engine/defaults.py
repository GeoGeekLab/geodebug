from geodebug.engine.registry import RuleRegistry
from geodebug.rules.crs.geo101 import MissingCRSRule
from geodebug.rules.crs.geo103 import GeographicCoordinateRangeRule
from geodebug.rules.crs.geo105 import CRSAreaOfUseRule
from geodebug.rules.operations.geo501 import AngularCRSBufferRule
from geodebug.rules.operations.geo502 import PlanarAreaOnGeographicCRSRule
from geodebug.rules.operations.geo503 import PlanarDistanceOnGeographicCRSRule
from geodebug.rules.raster.geo301 import InvalidRasterTransformRule
from geodebug.rules.raster.geo304 import NoDataMaskCollisionRule
from geodebug.rules.relations.geo402 import NoSpatialOverlapRule
from geodebug.rules.relations.geo404 import RasterGridMisalignmentRule
from geodebug.rules.vector.geo201 import InvalidGeometryRule


def build_default_registry() -> RuleRegistry:
    registry = RuleRegistry()
    registry.register(MissingCRSRule())
    registry.register(GeographicCoordinateRangeRule())
    registry.register(CRSAreaOfUseRule())
    registry.register(InvalidGeometryRule())
    registry.register(InvalidRasterTransformRule())
    registry.register(NoDataMaskCollisionRule())
    registry.register(NoSpatialOverlapRule())
    registry.register(RasterGridMisalignmentRule())
    registry.register(AngularCRSBufferRule())
    registry.register(PlanarAreaOnGeographicCRSRule())
    registry.register(PlanarDistanceOnGeographicCRSRule())
    return registry
