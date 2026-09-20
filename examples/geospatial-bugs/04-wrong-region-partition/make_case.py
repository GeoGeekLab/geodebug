from __future__ import annotations

import argparse
import json
from pathlib import Path


def _write(path: Path, payload: dict[str, object]) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def build_case(output_dir: Path) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)

    aoi = output_dir / "aoi_tokyo.geojson"
    detections = output_dir / "detections_sapporo.geojson"

    _write(
        aoi,
        {
            "type": "Feature",
            "properties": {"region": "tokyo", "batch": "2026-09-18"},
            "geometry": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [139.70, 35.64],
                        [139.82, 35.64],
                        [139.82, 35.73],
                        [139.70, 35.73],
                        [139.70, 35.64],
                    ]
                ],
            },
        },
    )

    _write(
        detections,
        {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {"id": "det-001", "region": "sapporo"},
                    "geometry": {"type": "Point", "coordinates": [141.3508, 43.0618]},
                },
                {
                    "type": "Feature",
                    "properties": {"id": "det-002", "region": "sapporo"},
                    "geometry": {"type": "Point", "coordinates": [141.3564, 43.0641]},
                },
                {
                    "type": "Feature",
                    "properties": {"id": "det-003", "region": "sapporo"},
                    "geometry": {"type": "Point", "coordinates": [141.3620, 43.0585]},
                },
            ],
        },
    )

    return aoi, detections


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    for path in build_case(args.output_dir):
        print(path)


if __name__ == "__main__":
    main()
