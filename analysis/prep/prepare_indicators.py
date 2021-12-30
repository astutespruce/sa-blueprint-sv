from pathlib import Path

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
