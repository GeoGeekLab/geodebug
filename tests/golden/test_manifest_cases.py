import json
import tomllib
from pathlib import Path

import pytest

from geodebug import check


MANIFEST = Path(__file__).with_name("cases.toml")


def _write_fixture(tmp_path: Path, name: str) -> Path:
    path = tmp_path / f"{name}.geojson"
    if name == "clean-point":
        geometry = {"type": "Point", "coordinates": [0, 0]}
    elif name == "invalid-latitude":
        geometry = {"type": "Point", "coordinates": [0, 95]}
    elif name == "invalid-bowtie":
        geometry = {
            "type": "Polygon",
            "coordinates": [[[0, 0], [1, 1], [1, 0], [0, 1], [0, 0]]],
        }
    else:
        raise AssertionError(f"unknown golden fixture: {name}")

    path.write_text(
        json.dumps({"type": "Feature", "properties": {}, "geometry": geometry}),
        encoding="utf-8",
    )
    return path


def _cases():
    with MANIFEST.open("rb") as handle:
        return tomllib.load(handle)["case"]


@pytest.mark.parametrize("case", _cases(), ids=lambda item: item["id"])
def test_golden_rule_manifest(case, tmp_path) -> None:
    target = _write_fixture(tmp_path, case["fixture"])

    report = check(target, deep=case["deep"])
    reported = {item.rule_id for item in report.diagnostics}

    assert reported == set(case["expected"])
    assert reported.isdisjoint(case["must_not_report"])
