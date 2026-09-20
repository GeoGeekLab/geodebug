from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import rasterio
from rasterio.transform import from_origin


def _write(path: Path, *, west: float, data: np.ndarray) -> None:
    with rasterio.open(
        path,
        "w",
        driver="GTiff",
        width=data.shape[1],
        height=data.shape[0],
        count=1,
        dtype=data.dtype,
        crs="EPSG:32654",
        transform=from_origin(west, 3_949_360.0, 10.0, 10.0),
    ) as dataset:
        dataset.write(data, 1)


def build_case(output_dir: Path) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    data = np.arange(32 * 32, dtype=np.uint16).reshape(32, 32)

    reference = output_dir / "reference.tif"
    candidate = output_dir / "candidate.tif"
    _write(reference, west=388_400.0, data=data)
    _write(candidate, west=388_405.0, data=data)
    return reference, candidate


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    for path in build_case(args.output_dir):
        print(path)


if __name__ == "__main__":
    main()
