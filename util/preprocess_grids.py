from pathlib import Path
import rasterio
import numpy as np

src_dir = Path("data")

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
for year in [2020, 2030, 2040, 2050, 2060, 2070, 2080, 2090, 2100]:
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


### Convert ecosystems to indexed
# original raster values
# values = {
#     6: "Upland hardwood",
#     8: "Pine and prairie",
#     10: "Freshwater marsh",
#     12: "Forested wetland",
#     14: "Waterbodies",
#     16: "Estuaries - estuarine marsh",
#     17: "Estuaries - open water",
#     18: "Beach and dune",
#     20: "Maritime forest",
#     22: "Marine",
# }

# mapped to value of ECOSYSTEMS (others not present are across region)
values_to_index = {6: 6, 8: 5, 10: 3, 12: 2, 14: 8, 16: 1, 17: 1, 18: 0, 20: 4, 22: 7}

with rasterio.open(
    src_dir / "EcosystemMask_20160229_Blueprint_2_1_AnalysisArea.tif"
) as src:
    data = src.read(1)
    for src_value, target_value in values_to_index.items():
        data[data == src_value] = target_value

    meta = src.meta.copy()
    meta["dtype"] = "uint8"

    with rasterio.open(src_dir / "ecosystems_indexed.tif", "w", **meta) as out:
        out.write(data.astype("uint8"), 1)
