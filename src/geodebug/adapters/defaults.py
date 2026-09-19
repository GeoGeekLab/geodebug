from geodebug.adapters.geojson import GeoJSONAdapter
from geodebug.adapters.geopandas import GeoPandasAdapter
from geodebug.adapters.parquet import GeoParquetAdapter
from geodebug.adapters.pyogrio import PyogrioAdapter
from geodebug.adapters.rasterio import RasterioAdapter
from geodebug.adapters.registry import AdapterRegistry


def build_default_adapter_registry() -> AdapterRegistry:
    registry = AdapterRegistry()
    registry.register(GeoPandasAdapter())
    registry.register(GeoJSONAdapter())
    registry.register(GeoParquetAdapter())
    registry.register(RasterioAdapter())
    registry.register(PyogrioAdapter())
    return registry
