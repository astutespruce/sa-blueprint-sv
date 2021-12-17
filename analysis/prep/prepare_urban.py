"""
Note: rasters are effectively in the same projection as EPSG:5070, but have slightly
different WKT.  These are set to match other rasters.

Note: rasters are pixel-aligned, no need to resample to match.
"""

import os
from pathlib import Path

import geopandas as gp
import pygeos as pg
import numpy as np
import rasterio
from rasterio.enums import Resampling

from analysis.constants import URBAN_YEARS, DATA_CRS, OVERVIEW_FACTORS
from analysis.lib.raster import create_lowres_mask, get_window


values = np.array(
    [0, 1, 25, 50, 100, 200, 300, 400, 500, 600, 700, 800, 900, 950, 975, 1000]
)


src_dir = Path("source_data")
out_dir = Path("data/inputs/threats/urban")

if not out_dir.exists():
    os.makedirs(out_dir)

# figure out clipping bounds
bnd = gp.read_feather("data/inputs/boundaries/sa_boundary.feather")
bounds = pg.total_bounds(bnd.geometry.values.data)

with rasterio.open(src_dir / "threats" / "serap_urb2020_IsNull0.tif") as src:
    window = get_window(src, bounds)
    transform = src.window_transform(window)


for year in URBAN_YEARS:
    print(f"Processing {year}...")

    filename = src_dir / "threats" / f"serap_urb{year}_IsNull0.tif"

    # need to convert values to index
    with rasterio.open(filename) as src:
        data = src.read(1, window=window)

        # convert values to index
        for index, value in enumerate(values):
            if index == 0:
                # leave 0 alone, it is NODATA or not urbanized
                continue

            data[data == value] = index

        meta = {
            "driver": "GTiff",
            "crs": DATA_CRS,
            "transform": transform,
            "width": data.shape[1],
            "height": data.shape[0],
            "count": 1,
            "nodata": 255,
            "dtype": "uint8",
            "compress": "lzw",
        }

        with rasterio.open(out_dir / f"urban_{year}.tif", "w", **meta) as out:
            out.write(data.astype("uint8"), 1)

            out.build_overviews(OVERVIEW_FACTORS, Resampling.nearest)

create_lowres_mask(
    out_dir / "urban_2100.tif", out_dir / "urban_mask.tif", factor=8, ignore_zero=True
)
