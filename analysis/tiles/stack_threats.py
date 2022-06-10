from pathlib import Path

import numpy as np
import pandas as pd
import rasterio
from rasterio.enums import Resampling
from rasterio.vrt import WarpedVRT

from analysis.constants import URBAN_YEARS
from analysis.lib.raster import add_overviews
from analysis.lib.io import write_raster

URBAN_THRESHOLD = 12  # probability = 0.9


data_dir = Path("data/inputs")
src_dir = data_dir / "threats"
tmp_dir = Path("/tmp")
out_dir = Path("data/for_tiles")
blueprint_filename = data_dir / "blueprint2021.tif"
vrt_filename = src_dir / "slr" / "slr.vrt"

# NOTE: both threats datasets use different resolutions than the blueprint

# NOTE:

# Codes:
# 0: not projected to urbanize
# 1: already urbanized by 2009
# 2: 90% likely to urbanize by 2020 # (TODO: revisit)
# ...
# 10: 90% likely to urbanize by 2100

data = None
for i, year in enumerate(URBAN_YEARS[::-1]):
    print(f"processing {year}")
    value = (len(URBAN_YEARS) - i) + 1
    src = rasterio.open(src_dir / "urban" / f"urban_{year}.tif")
    nodata = int(src.nodata)
    urban = src.read(1)

    if data is None:
        data = np.zeros_like(urban)
        data[urban == nodata] = nodata
        data[urban == 1] = 1  # pixel is already urban if value 1 in 2020

    # overwrite with the earliest date that the pixel is projected to urbanize
    data[(urban >= URBAN_THRESHOLD) & (urban < src.nodata)] = value

# write temporary file so we can read in via VRT
filename = tmp_dir / "stacked_urban.tif"
write_raster(
    filename,
    data,
    transform=src.transform,
    crs=src.crs,
    nodata=nodata,
)
src = rasterio.open(filename)

### Extract to match the blueprint
blueprint = rasterio.open(blueprint_filename)
nodata = int(blueprint.nodata)
mask = blueprint.read(1) == nodata

with WarpedVRT(
    src,
    width=blueprint.width,
    height=blueprint.height,
    nodata=nodata,
    transform=blueprint.transform,
    resampling=Resampling.nearest,
) as vrt:
    data = vrt.read()[0]

# mask out to match Blueprint data pixels
data[mask] = nodata

outfilename = out_dir / "stacked_urban_30m.tif"
write_raster(
    outfilename,
    data,
    transform=blueprint.transform,
    crs=blueprint.crs,
    nodata=nodata,
)

add_overviews(outfilename)

### Extract SLR to match the blueprint
src = rasterio.open(vrt_filename)
with WarpedVRT(
    src,
    width=blueprint.width,
    height=blueprint.height,
    nodata=nodata,
    transform=blueprint.transform,
    resampling=Resampling.nearest,
) as vrt:
    data = vrt.read()[0]

# mask out to match Blueprint data pixels
data[mask] = nodata


outfilename = out_dir / "slr_30m.tif"
write_raster(
    outfilename,
    data,
    transform=blueprint.transform,
    crs=blueprint.crs,
    nodata=nodata,
)

add_overviews(outfilename)
