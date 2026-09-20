from __future__ import annotations

import argparse
from pathlib import Path

import rasterio


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()

    with rasterio.open(args.data_dir / "surface_class.tif") as dataset:
        data = dataset.read(1)
        valid_by_nodata = data != dataset.nodata
        valid_by_mask = dataset.read_masks(1) > 0

    print(f"valid_by_nodata={int(valid_by_nodata.sum())}")
    print(f"valid_by_mask={int(valid_by_mask.sum())}")
    print(f"zero_pixel_nodata_valid={bool(valid_by_nodata[0, 0])}")
    print(f"zero_pixel_mask_valid={bool(valid_by_mask[0, 0])}")


if __name__ == "__main__":
    main()
