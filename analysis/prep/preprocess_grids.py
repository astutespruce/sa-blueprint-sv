from pathlib import Path
import rasterio
from rasterio.features import rasterize
from rasterio.enums import Resampling
from rasterio.vrt import WarpedVRT
import numpy as np
from pyogrio.geopandas import read_dataframe

from analysis.pygeos_util import to_dict_all
from analysis.constants import URBAN_YEARS

src_dir = Path("source_data")
out_dir = Path("data/inputs")

### Bin SLR to 1 foot increments up to 6 feet
slr_filename = src_dir / "threats" / f"slra_alb30m_IsNull0.tif"
src = rasterio.open(slr_filename)
data = src.read(1, masked=True)

# everything >= 6ft gets binned at 6 ft
data[data > 60] = 60

# round up to nearest foot
data = np.round(data / 10, 0).astype("int8")

with rasterio.open(src_dir / "threats" / "slr_binned.tif", "w", **src.meta) as out:
    out.write(data, 1)


### convert urbanization to indexed for easier bincounts later
values = np.array(
    [0, 1, 25, 50, 100, 200, 300, 400, 500, 600, 700, 800, 900, 950, 975, 1000]
)
for year in URBAN_YEARS:
    print(f"Processing {year}...")

    filename = src_dir / "threats" / f"serap_urb{year}_IsNull0.tif"

    # need to convert values to index
    with rasterio.open(filename) as src:
        data = src.read(1)

        # convert values to index
        for index, value in enumerate(values):
            if index == 0:
                # leave 0 alone, it is NODATA or not urbanized
                continue

            data[data == value] = index

        meta = src.meta.copy()
        meta["dtype"] = "uint8"

        with rasterio.open(
            src_dir / "threats" / f"urb_indexed_{year}.tif", "w", **meta
        ) as out:
            out.write(data.astype("uint8"), 1)


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
