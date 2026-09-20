from __future__ import annotations

import argparse
import warnings
from pathlib import Path

import geopandas as gpd


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()

    roads = gpd.read_file(args.data_dir / "road_segment.geojson")

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        buffers = roads.geometry.buffer(500)

    bounds = tuple(round(float(value), 3) for value in buffers.total_bounds)
    print(f"buffers={len(buffers)}")
    print(f"bounds={bounds}")
    print(f"warnings={len(caught)}")
    if caught:
        print(f"first_warning={caught[0].message}")


if __name__ == "__main__":
    main()
