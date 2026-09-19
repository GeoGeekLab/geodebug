import pytest

rasterio = pytest.importorskip("rasterio")
from rasterio.transform import from_origin

from geodebug import compare, inspect
from geodebug.facts.keys import RASTER_RESOLUTION


def _write_raster(path, *, west: float) -> None:
    import numpy as np

    data = np.ones((1, 10, 10), dtype="uint8")
    with rasterio.open(
        path,
        "w",
        driver="GTiff",
        width=10,
        height=10,
        count=1,
        dtype="uint8",
        crs="EPSG:32648",
        transform=from_origin(west, 100.0, 10.0, 10.0),
    ) as dataset:
        dataset.write(data)


def test_rasterio_adapter_reads_grid_metadata(tmp_path) -> None:
    path = tmp_path / "grid.tif"
    _write_raster(path, west=0.0)

    snapshot = inspect(path)

    assert snapshot.subject.adapter == "rasterio"
    assert snapshot.facts.require(RASTER_RESOLUTION).value == (10.0, 10.0)


def test_compare_detects_half_pixel_raster_misalignment(tmp_path) -> None:
    left = tmp_path / "left.tif"
    right = tmp_path / "right.tif"
    _write_raster(left, west=0.0)
    _write_raster(right, west=5.0)

    report = compare(left, right)

    ids = [diagnostic.rule_id for diagnostic in report.diagnostics]
    assert "GEO404" in ids
