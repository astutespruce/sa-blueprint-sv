from pathlib import Path

import numpy as np
import rasterio


src_dir = Path("source_data/original_indicators")
out_dir = Path("data/inputs/indicators")


### Remove 0 values from greenways
# This is so that when we make overviews, these are not mostly removed
# (they are from linear features)

filename = "GreenwaysAndTrails.tif"
print("Processing", filename)
with rasterio.open(src_dir / filename) as src:
    data = src.read(1)
    data[data == 0] = src.nodata

    with rasterio.open(out_dir / filename, "w+", **src.profile) as out:
        out.write_band(1, data)

### Shift values of Migratory fish connectivity to start at 0

filename = "MigratoryFishConnectivity.tif"
print("Processing", filename)
with rasterio.open(src_dir / filename) as src:
    data = src.read(1)
    data = np.where(data == src.nodata, int(src.nodata), data - 1)

    with rasterio.open(out_dir / filename, "w+", **src.profile) as out:
        out.write_band(1, data)
