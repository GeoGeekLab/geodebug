from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import rasterio


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()

    with (
        rasterio.open(args.data_dir / "reference.tif") as reference,
        rasterio.open(args.data_dir / "candidate.tif") as candidate,
    ):
        left = reference.read(1)
        right = candidate.read(1)
        mean_abs_diff = np.abs(left.astype(np.int64) - right.astype(np.int64)).mean()

        print(f"same_crs={reference.crs == candidate.crs}")
        print(f"same_shape={left.shape == right.shape}")
        print(f"same_resolution={reference.res == candidate.res}")
        print(f"same_transform={reference.transform == candidate.transform}")
        print(f"mean_abs_pixel_diff={mean_abs_diff:.1f}")


if __name__ == "__main__":
    main()
