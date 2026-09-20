from __future__ import annotations

import argparse
import json
from pathlib import Path


def build_case(output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "road_segment.geojson"
    payload = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {
                    "road_id": "tokyo-station-east",
                    "status": "closed",
                },
                "geometry": {
                    "type": "LineString",
                    "coordinates": [
                        [139.7667, 35.6808],
                        [139.7681, 35.6817],
                    ],
                },
            }
        ],
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    path = build_case(args.output_dir)
    print(path)


if __name__ == "__main__":
    main()
