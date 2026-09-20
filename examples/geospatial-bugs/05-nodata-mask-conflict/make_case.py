from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import rasterio
from rasterio.transform import from_origin


def build_case(output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "surface_class.tif"

    data = np.array(
        [
            [0, 1, 1, 1],
            [1, 2, 2, 1],
            [1, 2, 3, 1],
            [1, 1, 1, 1],
        ],
        dtype=np.uint8,
    )

    with rasterio.open(
        path,
        "w",
        driver="GTiff",
        width=4,
        height=4,
        count=1,
        dtype=data.dtype,
        crs="EPSG:32654",
        nodata=0,
        transform=from_origin(388_400.0, 3_949_360.0, 10.0, 10.0),
    ) as dataset:
        dataset.write(data, 1)
        dataset.write_mask(np.full((4, 4), 255, dtype=np.uint8))

    return path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    path = build_case(args.output_dir)
    print(path)


if __name__ == "__main__":
    main()
