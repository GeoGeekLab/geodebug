from __future__ import annotations

import argparse
from pathlib import Path

import geopandas as gpd


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()

    aoi = gpd.read_file(args.data_dir / "aoi_tokyo.geojson")
    detections = gpd.read_file(args.data_dir / "detections_sapporo.geojson")
    joined = gpd.sjoin(detections, aoi, how="inner", predicate="within")

    print(f"detections_in={len(detections)}")
    print(f"joined_rows={len(joined)}")
    print("pipeline_status=success")


if __name__ == "__main__":
    main()
