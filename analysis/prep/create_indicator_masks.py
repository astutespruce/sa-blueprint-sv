"""
Construct a coarse resolution mask (roughly 480m) for each indicator to determine when a given area
has pixel values that should be read from the 30m data.
"""


from pathlib import Path
from math import ceil

import geopandas as gp
from affine import Affine
import rasterio
from rasterio.enums import Resampling
from rasterio.vrt import WarpedVRT

from analysis.constants import INDICATORS

factor = 16


src_dir = Path("data/inputs/indicators")
out_dir = src_dir / "masks"

for indicator in INDICATORS:
    print(f"Processing {indicator['id']}...")

    filename = src_dir / indicator["filename"]

    with rasterio.open(filename) as src:
        nodata = src.nodatavals[0]
        width = ceil(src.width / factor)
        height = ceil(src.height / factor)
        dst_transform = src.transform * Affine.scale(
            src.width / width, src.height / height
        )

        with WarpedVRT(
            src,
            width=width,
            height=height,
            nodata=nodata,
            transform=dst_transform,
            resampling=Resampling.max,
        ) as vrt:

            data = vrt.read()

            # for many indicators, 0 is the background value so leave it intact
            data[data != nodata] = 1

            meta = src.profile.copy()
            meta.update({"width": width, "height": height, "transform": dst_transform})

            with rasterio.open(out_dir / filename.name, "w", **meta) as out:
                out.write(data)

