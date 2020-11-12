from pathlib import Path
from math import ceil, log2

from progress.bar import Bar
import numpy as np
import pandas as pd
import rasterio
import geopandas as gp
import pygeos as pg

from analysis.constants import INDICATORS
from analysis.lib.io import write_raster
from analysis.lib.raster import add_overviews

data_dir = Path("data/inputs")
src_dir = data_dir / "indicators"
out_dir = Path("data/for_tiles")
blueprint_filename = data_dir / "blueprint2020.tif"
bnd_filename = data_dir / "boundaries/sa_boundary.feather"


# group marine and beach types
groups = [
    [
        "freshwater_imperiledaquaticspecies",
        "freshwater_migratoryfishconnectivity",
        "freshwater_networkcomplexity",
        "freshwater_permeablesurface",
        "freshwater_riparianbuffers",
        "land_amphibianreptiles",
        "land_forestbirds",
    ],
    [
        "land_beachbirds",
        "land_resilientcoastalsites",
        "land_unalteredbeach",
        "marine_birds",
        "marine_estuarinecondition",
        "marine_mammals",
    ],
    [],
]


df = pd.DataFrame(
    [
        [
            e["id"].split("_")[0],
            e["id"],
            e["filename"],
            len(e["values"]),
            min([v["value"] for v in e["values"]]),
        ]
        for e in INDICATORS
    ],
    columns=["ecosystem", "id", "filename", "num_values", "min_value"],
).set_index("id")
df["bits"] = df.num_values.apply(lambda x: ceil(log2(max(x, 2))))
df["ignore_0"] = df.min_value == 0
df["src"] = df.filename.apply(lambda x: rasterio.open(src_dir / x))
df["nodata"] = df.src.apply(lambda src: int(src.nodata))

for i, ids in enumerate(groups):
    df.loc[df.index.isin(ids), "group"] = i

# df.group = df.group.astype("uint8")
df[["group", "bits"]].reset_index().to_feather(out_dir / "encoding.feather")


### determine the windows that overlap bounds
# everything else will be filled with 0
print("Calculating overlapping windows")
bnd = gp.read_feather(bnd_filename).geometry.values.data[0]

blueprint = rasterio.open(blueprint_filename)
windows = np.array([w for _, w in blueprint.block_windows(1)])
bounds = np.array([blueprint.window_bounds(w) for w in windows]).T
bounds = pg.box(*bounds)
tree = pg.STRtree(bounds)
ix = tree.query(bnd, predicate="intersects")
ix.sort()
windows = windows[ix]

for i, group in enumerate(groups):

    rows = df.loc[df.index.isin(group)]
    total_bits = rows.bits.sum() + len(rows)
    print(f"Total bits needed: {total_bits}")

    encoding = {
        "bits": total_bits,
        "layers": rows[["bits"]].reset_index().to_dict(orient="records"),
    }

    rgb = np.zeros(shape=blueprint.shape + (3,), dtype="uint8")

    for window in Bar(f"Processing group {i}...", max=len(windows)).iter(windows):
        # nodata_mask = blueprint.read(1, window=window) == int(blueprint.nodata)

        masks = []
        layer_bits = []
        for id in group:
            row = rows.loc[id]

            data = row.src.read(1, window=window)

            # extract presence mask
            if row.ignore_0:
                mask = (data != row.nodata) & (data != 0)

            else:
                mask = data != row.nodata

            masks.append(mask)

            # set nodata pixels to 0
            data[~mask] = 0

            # the inner unpack must be in big bit order to get bits in right direction
            bits = np.unpackbits(data, bitorder="big").reshape(data.shape + (8,))[
                :, :, -row.bits :
            ]
            layer_bits.append(bits)

        # if masks are all false for this window, we can skip this step
        if not np.asarray(masks).sum():
            continue

        # stack mask bits and layer_bits along inner dimension so that we have a shape of
        # (height, width, total_bits)
        data_bits = np.dstack(masks + layer_bits)

        # packbits must be in little order to read the whole array properly in JS
        packed = np.squeeze(np.packbits(data_bits, axis=-1, bitorder="little"))

        # There may or may not have all components of rgb, and they are inverse order
        # read them into out in reverse order
        row_slice, col_slice = window.toslices()
        for j in range(packed.shape[-1]):
            rgb[row_slice, col_slice, 2 - j] = packed[:, :, j]

    outfilename = out_dir / f"indicators_{i}.tif"
    write_raster(
        outfilename,
        rgb,
        transform=blueprint.transform,
        crs=blueprint.crs,
        nodata=255,
        photometric="RGB",
    )

    add_overviews(outfilename)
