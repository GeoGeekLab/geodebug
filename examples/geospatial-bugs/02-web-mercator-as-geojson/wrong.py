from __future__ import annotations

import argparse
import json
from pathlib import Path

from shapely.geometry import shape


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()

    payload = json.loads((args.data_dir / "station.geojson").read_text(encoding="utf-8"))
    geometry = shape(payload["geometry"])

    print(f"geometry_type={geometry.geom_type}")
    print(f"geometry_valid={geometry.is_valid}")
    print(f"x={geometry.x:.2f}")
    print(f"y={geometry.y:.2f}")


if __name__ == "__main__":
    main()
