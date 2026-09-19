import pytest
from shapely.geometry import Point

from geodebug import inspect


def _frame():
    geopandas = pytest.importorskip("geopandas")
    return geopandas.GeoDataFrame(
        {"value": [1, 2]},
        geometry=[Point(0, 0), Point(1, 1)],
        crs="EPSG:4326",
    )


def test_geopandas_in_memory_adapter() -> None:
    snapshot = inspect(_frame())

    assert snapshot.subject.adapter == "geopandas"


def test_pyogrio_file_adapter(tmp_path) -> None:
    pytest.importorskip("pyogrio")
    path = tmp_path / "points.gpkg"
    _frame().to_file(path, driver="GPKG")

    snapshot = inspect(path)

    assert snapshot.subject.adapter == "pyogrio"


def test_geoparquet_adapter(tmp_path) -> None:
    pytest.importorskip("pyarrow")
    path = tmp_path / "points.parquet"
    _frame().to_parquet(path)

    snapshot = inspect(path)

    assert snapshot.subject.adapter == "geoparquet"
