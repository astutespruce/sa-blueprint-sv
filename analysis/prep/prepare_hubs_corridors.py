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
inland_hubs = read_dataframe(corridors_dir / "InlandHubs2021.shp")
marine_hubs = read_dataframe(corridors_dir / "MarineEstuarineHubs2021.shp")


# The rasters have the same footprint and are 90m; raster / resample to 30m to
# match Blueprint
with rasterio.open(out_dir / "blueprint2021.tif") as blueprint, rasterio.open(
    corridors_dir / "InlandCorridors2021.tif"
) as inland, rasterio.open(
    corridors_dir / "MarineEstuarineCorridors2021.tif"
) as marine:
    print("Rasterizing hubs...")
    # rasterize hubs to match inland
    inland_hubs_data = rasterize(
        to_dict_all(inland_hubs.geometry.values.data),
        blueprint.shape,
        transform=blueprint.transform,
        dtype="uint8",
    )
    marine_hubs_data = rasterize(
        to_dict_all(marine_hubs.geometry.values.data),
        blueprint.shape,
        transform=blueprint.transform,
        dtype="uint8",
    )

    # Resample inland and marine data
    print("Reading and warping inland corridors...")
    vrt = WarpedVRT(
        inland,
        width=blueprint.width,
        height=blueprint.height,
        nodata=blueprint.nodata,
        transform=blueprint.transform,
        resampling=Resampling.nearest,
    )
    inland_data = vrt.read()[0]

    print("Reading and warping marine corridors...")
    vrt = WarpedVRT(
        marine,
        width=blueprint.width,
        height=blueprint.height,
        nodata=blueprint.nodata,
        transform=blueprint.transform,
        resampling=Resampling.nearest,
    )
    marine_data = vrt.read()[0]

    # consolidate all values into a single raster, writing hubs over corridors
    data = np.ones(shape=blueprint.shape, dtype="uint8") * 255
    data[inland_data == 1] = 1
    data[marine_data == 1] = 3
    data[inland_hubs_data == 1] = 0
    data[marine_hubs_data == 1] = 2

    # stamp back in nodata from Blueprint
    blueprint_data = blueprint.read(1)
    data[blueprint_data == 255] = 255

    meta = blueprint.profile.copy()
    meta["dtype"] = "uint8"
    meta["nodata"] = 255

    with rasterio.open(out_dir / "corridors.tif", "w", **meta) as out:
        out.write(data.astype("uint8"), 1)

