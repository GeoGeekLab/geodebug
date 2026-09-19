from pyproj import CRS, Transformer

from geodebug.facts.crs import build_crs_facts
from geodebug.facts.keys import SPATIAL_BOUNDS
from geodebug.models.enums import RuleState
from geodebug.models.facts import FactRecord
from geodebug.rules.crs.geo105 import CRSAreaOfUseRule


def _projected_context(make_context, lon: float, lat: float):
    crs = CRS.from_epsg(32648)
    transformer = Transformer.from_crs("OGC:CRS84", crs, always_xy=True)
    x, y = transformer.transform(lon, lat)
    facts = [
        *build_crs_facts(crs.to_wkt(), origin="test", method="fixture"),
        FactRecord.known(
            SPATIAL_BOUNDS,
            (x - 1000.0, y - 1000.0, x + 1000.0, y + 1000.0),
        ),
    ]
    return make_context(facts=facts)


def test_geo105_passes_inside_area_of_use(make_context) -> None:
    context = _projected_context(make_context, 103.8, 1.3)

    assert CRSAreaOfUseRule().evaluate(context).state is RuleState.PASS


def test_geo105_fails_outside_area_of_use(make_context) -> None:
    context = _projected_context(make_context, 120.0, 1.3)

    assert CRSAreaOfUseRule().evaluate(context).state is RuleState.FAIL


def test_geo105_geographic_crs_is_not_applicable(make_context) -> None:
    facts = [
        *build_crs_facts("OGC:CRS84", origin="test", method="fixture"),
        FactRecord.known(SPATIAL_BOUNDS, (0.0, 0.0, 1.0, 1.0)),
    ]

    assert CRSAreaOfUseRule().evaluate(make_context(facts=facts)).state is RuleState.NOT_APPLICABLE
