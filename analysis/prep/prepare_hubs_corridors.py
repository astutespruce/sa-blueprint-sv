from pathlib import Path
import rasterio
from rasterio.features import rasterize
from rasterio.enums import Resampling
from rasterio.vrt import WarpedVRT
import numpy as np
from pyogrio.geopandas import read_dataframe

from analysis.lib.pygeos_util import to_dict_all

src_dir = Path("source_data")
out_dir = Path("data/inputs")


### Rasterize and merge hubs and corridors
print("Processing hubs & corridors")
corridors_dir = src_dir / "corridors"
inland_hubs = read_dataframe(corridors_dir / "TerrestrialHubs.shp")
marine_hubs = read_dataframe(corridors_dir / "MarineHubs.shp")


# The rasters have the same footprint, but inland is at 30m and marine is at 200m
with rasterio.open(corridors_dir / "TerrestrialCorridors.tif") as inland, rasterio.open(
    corridors_dir / "MarineCorridors.tif"
) as marine:
    print("Rasterizing hubs...")
    # rasterize hubs to match inland
    inland_hubs_data = rasterize(
        to_dict_all(inland_hubs.geometry.values.data),
        inland.shape,
        transform=inland.transform,
        dtype="uint8",
    )
    marine_hubs_data = rasterize(
        to_dict_all(marine_hubs.geometry.values.data),
        inland.shape,
        transform=inland.transform,
        dtype="uint8",
    )

    inland_data = inland.read(1)

    # Marine data must be resampled to 30m with matching offset to inland
    vrt = WarpedVRT(
        marine,
        width=inland.width,
        height=inland.height,
        nodata=marine.nodata,
        transform=inland.transform,
        resampling=Resampling.nearest,
    )
    print("Reading and warping marine corridors...")

    marine_data = vrt.read()[0]

    # consolidate all values into a single raster, writing hubs over corridors
    data = np.ones(shape=inland_data.shape, dtype="uint8") * 255
    data[inland_data == 1] = 1
    data[marine_data == 1] = 3
    data[inland_hubs_data == 1] = 0
    data[marine_hubs_data == 1] = 2

    meta = inland.profile.copy()
    meta["dtype"] = "uint8"
    meta["nodata"] = 255

    with rasterio.open(out_dir / "corridors.tif", "w", **meta) as out:
        out.write(data.astype("uint8"), 1)

########
with rasterio.open("/tmp/inland.tif", "w", **inland.profile) as out:
    out.write_band(1, inland_hubs_data)

with rasterio.open("/tmp/marine.tif", "w", **inland.profile) as out:
    out.write_band(1, marine_hubs_data)
