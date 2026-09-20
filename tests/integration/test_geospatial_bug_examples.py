from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from geodebug import check, compare, preflight

CASES = Path(__file__).resolve().parents[2] / "examples" / "geospatial-bugs"


def _run(script: Path, flag: str, directory: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(script), flag, str(directory)],
        check=True,
        capture_output=True,
        text=True,
    )


def _generate(case: str, tmp_path: Path) -> None:
    _run(CASES / case / "make_case.py", "--output-dir", tmp_path)


def _wrong(case: str, tmp_path: Path) -> subprocess.CompletedProcess[str]:
    return _run(CASES / case / "wrong.py", "--data-dir", tmp_path)


def _rule_ids(report) -> list[str]:
    return [diagnostic.rule_id for diagnostic in report.diagnostics]


def test_buffer_in_degrees_runs_then_geo501_fails(tmp_path: Path) -> None:
    pytest.importorskip("geopandas")
    case = "01-buffer-in-degrees"
    _generate(case, tmp_path)

    result = _wrong(case, tmp_path)
    assert "buffers=1" in result.stdout

    report = preflight(
        tmp_path / "road_segment.geojson",
        operation="buffer",
        parameters={"distance": 500},
    )
    assert "GEO501" in _rule_ids(report)


def test_web_mercator_geojson_runs_then_geo103_fails(tmp_path: Path) -> None:
    case = "02-web-mercator-as-geojson"
    _generate(case, tmp_path)

    result = _wrong(case, tmp_path)
    assert "geometry_valid=True" in result.stdout

    report = check(tmp_path / "station.geojson")
    assert _rule_ids(report) == ["GEO103"]


def test_half_pixel_shift_runs_then_geo404_fails(tmp_path: Path) -> None:
    pytest.importorskip("rasterio")
    case = "03-half-pixel-shift"
    _generate(case, tmp_path)

    result = _wrong(case, tmp_path)
    assert "mean_abs_pixel_diff=0.0" in result.stdout
    assert "same_transform=False" in result.stdout

    report = compare(tmp_path / "reference.tif", tmp_path / "candidate.tif")
    assert "GEO404" in _rule_ids(report)


def test_wrong_region_partition_runs_then_geo402_fails(tmp_path: Path) -> None:
    pytest.importorskip("geopandas")
    case = "04-wrong-region-partition"
    _generate(case, tmp_path)

    result = _wrong(case, tmp_path)
    assert "joined_rows=0" in result.stdout
    assert "pipeline_status=success" in result.stdout

    report = compare(
        tmp_path / "aoi_tokyo.geojson",
        tmp_path / "detections_sapporo.geojson",
    )
    assert "GEO402" in _rule_ids(report)


def test_nodata_mask_conflict_runs_then_geo304_fails(tmp_path: Path) -> None:
    pytest.importorskip("rasterio")
    case = "05-nodata-mask-conflict"
    _generate(case, tmp_path)

    result = _wrong(case, tmp_path)
    assert "valid_by_nodata=15" in result.stdout
    assert "valid_by_mask=16" in result.stdout

    report = check(tmp_path / "surface_class.tif", deep=True)
    assert "GEO304" in _rule_ids(report)
