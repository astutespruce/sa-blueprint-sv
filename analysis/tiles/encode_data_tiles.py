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


# very small amount added to numbers to make sure that log2 gives us current number of bytes
EPS = 1e-6


### Create groups to contain indicators up to 24 bits each
groups = [
    [
        "freshwater_imperiledaquaticspecies",
        "freshwater_migratoryfishconnectivity",
        "freshwater_networkcomplexity",
        "freshwater_permeablesurface",
        "freshwater_riparianbuffers",
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
    [
        "land_forestedwetlandextent",
        "land_greenways",
        "land_intactcores",
        "land_lowurbanhistoric",
        "land_maritimeforestextent",
        "land_marshpatchsize",
        "land_pinebirds",
    ],
    [
        "land_amphibianreptiles",
        "land_resilientterrestrialsites",
        "land_urbanopenspace",
        "marine_potentialhardbottomcondition",
        "land_marshextent",
        "land_previouslyburnedhabitat",
    ],
]


### Create dataframe with info about bits required, groups, etc
df = pd.DataFrame(
    [
        [
            e["id"].split("_")[0],
            e["id"],
            e["filename"],
            min([v["value"] for v in e["values"]]),
            max([v["value"] for v in e["values"]]),
        ]
        for e in INDICATORS
    ],
    columns=["ecosystem", "id", "filename", "min_value", "max_value"],
).set_index("id")
df["bits"] = df.max_value.apply(lambda x: ceil(log2(max(x, 2) + EPS)))
# if min value declared is > 0, then we aren't showing those 0 values elsewhere
df["ignore_0"] = df.min_value > 0
df["src"] = df.filename.apply(lambda x: rasterio.open(src_dir / x))
df["nodata"] = df.src.apply(lambda src: int(src.nodata))

for i, ids in enumerate(groups):
    df.loc[df.index.isin(ids), "group"] = i

df.group = df.group.astype("uint8")
df[["group", "bits"]].reset_index().to_feather(out_dir / "encoding.feather")

print("Planned bits per layer")
print(df.groupby("group").size() + df.groupby("group").bits.sum())


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


window_shape = (windows[0].height, windows[0].width)

# create array for filling up to 32 bit
fill = np.zeros(shape=window_shape, dtype="uint8")


for i, group in enumerate(groups):
    rows = df.loc[df.index.isin(group)]
    total_bits = rows.bits.sum() + len(rows)

    if total_bits > 24:
        raise ValueError("Bits per group must be <= 24")

    # Find least number of bands that will hold the encoded data
    if total_bits <= 8:
        dtype = "uint8"
        num_bytes = 1

    elif total_bits > 8 and total_bits <= 16:
        dtype = "uint16"
        num_bytes = 2

    else:
        dtype = "uint32"
        num_bytes = 4

    out = np.zeros(shape=blueprint.shape, dtype=dtype)

    # FIXME:
    windows = windows[40598:40599]

    for window in Bar(
        f"Processing group {i} ({total_bits} bits)", max=len(windows)
    ).iter(windows):
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
        # then convert from BGR order to RGB order
        packed = np.squeeze(np.packbits(data_bits, axis=-1, bitorder="little"))[
            ..., ::-1
        ]

        # fill remaining bytes up to dtype bytes
        # packed values are in BGR order, invert them
        encoded = np.dstack([packed] + ([fill] * (num_bytes - packed.shape[-1])))
        out[window.toslices()] = encoded.view(dtype).reshape(window_shape)

    # FIXME:
    transform = blueprint.window_transform(window)
    out = encoded.view(dtype).reshape(window_shape).copy()

    # transform = blueprint.transform

    outfilename = out_dir / f"indicators_{i}.tif"
    write_raster(outfilename, out, transform=transform, crs=blueprint.crs, nodata=0)

    add_overviews(outfilename)
