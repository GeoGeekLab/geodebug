import json

from geodebug import check, compare, inspect
from geodebug.facts.keys import CRS_KIND, VECTOR_INVALID_GEOMETRY_COUNT
from geodebug.models.enums import FactState, SubjectKind


def _write_geojson(path, coordinates) -> None:
    payload = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [coordinates],
                },
            }
        ],
    }
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_geojson_inspect_normalizes_crs_and_geometry_facts(tmp_path) -> None:
    path = tmp_path / "valid.geojson"
    _write_geojson(path, [[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]])

    snapshot = inspect(path)

    assert snapshot.subject.kind is SubjectKind.VECTOR
    assert snapshot.subject.adapter == "geojson"
    assert snapshot.facts.require(CRS_KIND).value == "geographic"
    assert snapshot.facts.require(VECTOR_INVALID_GEOMETRY_COUNT).state is FactState.UNKNOWN


def test_geojson_deep_check_detects_invalid_geometry(tmp_path) -> None:
    path = tmp_path / "bowtie.geojson"
    _write_geojson(path, [[0, 0], [1, 1], [1, 0], [0, 1], [0, 0]])

    report = check(path, deep=True)

    assert [diagnostic.rule_id for diagnostic in report.diagnostics] == ["GEO201"]


def test_compare_detects_non_overlapping_extents(tmp_path) -> None:
    left = tmp_path / "left.geojson"
    right = tmp_path / "right.geojson"
    _write_geojson(left, [[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]])
    _write_geojson(right, [[10, 10], [11, 10], [11, 11], [10, 11], [10, 10]])

    report = compare(left, right)

    assert [diagnostic.rule_id for diagnostic in report.diagnostics] == ["GEO402"]
    assert report.diagnostics[0].subject_ids == [
        f"file:{left.as_posix()}",
        f"file:{right.as_posix()}",
    ]
