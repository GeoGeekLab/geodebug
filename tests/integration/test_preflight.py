import json

from geodebug import preflight


def test_preflight_detects_planar_area_on_geojson(tmp_path) -> None:
    path = tmp_path / "polygon.geojson"
    path.write_text(
        json.dumps(
            {
                "type": "Polygon",
                "coordinates": [[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]],
            }
        ),
        encoding="utf-8",
    )

    report = preflight(path, operation="area")

    ids = [diagnostic.rule_id for diagnostic in report.diagnostics]
    assert ids == ["GEO502"]
