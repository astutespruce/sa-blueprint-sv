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

