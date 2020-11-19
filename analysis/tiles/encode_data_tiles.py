from pathlib import Path
from math import ceil, log2

from progress.bar import Bar
import numpy as np
import pandas as pd
import rasterio
from rasterio.windows import get_data_window
import geopandas as gp
import pygeos as pg


from analysis.constants import INDICATORS, CORRIDORS
from analysis.lib.io import write_raster
from analysis.lib.raster import add_overviews

data_dir = Path("data/inputs")
src_dir = data_dir / "indicators"
out_dir = Path("data/for_tiles")
blueprint_filename = data_dir / "blueprint2020.tif"
corridors_filename = data_dir / "corridors.tif"
bnd_filename = data_dir / "boundaries/sa_boundary.feather"


# very small amount added to numbers to make sure that log2 gives us current number of bytes
EPS = 1e-6


### Create groups to contain indicators and corridors up to 24 bits each
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
        "marine_birds",
        "marine_estuarinecondition",
        "marine_mammals",
        "marine_potentialhardbottomcondition",
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
        "land_unalteredbeach",
        "land_marshextent",
        "land_previouslyburnedhabitat",
        "corridors",
    ],
]


### Create dataframe with info about bits required, groups, etc
df = pd.DataFrame(
    [
        [
            e["id"].split("_")[0],
            e["id"],
            src_dir / e["filename"],
            min([v["value"] for v in e["values"]]),
            max([v["value"] for v in e["values"]]),
        ]
        for e in INDICATORS
    ],
    columns=["ecosystem", "id", "filename", "min_value", "max_value"],
)
df = df.append(
    {
        "ecosystem": "",
        "id": "corridors",
        "filename": corridors_filename,
        "min_value": 0,
        "max_value": 3,
    },
    ignore_index=True,
    sort=False,
)
df = df.set_index("id")

df["bits"] = df.max_value.apply(lambda x: ceil(log2(max(x, 2) + EPS)))
# if min value declared is > 0, then we aren't showing those 0 values elsewhere
df["ignore_0"] = df.min_value > 0
df["src"] = df.filename.apply(lambda x: rasterio.open(x))
df["nodata"] = df.src.apply(lambda src: int(src.nodata))

for i, ids in enumerate(groups):
    df.loc[df.index.isin(ids), "group"] = i

df.group = df.group.astype("uint8")

# NOTE: groups must be stored in encoding definition
# in exactly the same order they are encoded
df[["group", "bits"]].reset_index().to_feather(out_dir / "encoding.feather")

print("Planned bits per group")
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

for i in sorted(df.group.unique()):
    rows = df.loc[df.group == i]
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
    # windows = windows[57469:]

    for window in Bar(
        f"Processing group {i} ({total_bits} bits)", max=len(windows)
    ).iter(windows):
        masks = []
        layer_bits = []
        for id in rows.index:
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

        window_shape = (window.height, window.width)

        # fill remaining bytes up to dtype bytes
        fill = np.zeros(shape=window_shape, dtype="uint8")

        encoded = np.dstack([packed] + ([fill] * (num_bytes - packed.shape[-1])))
        out[window.toslices()] = encoded.view(dtype).reshape(window_shape)

    # determine the window where data are available, and write out a smaller output
    print("Calculating data window...")
    data_window = get_data_window(out, nodata=0)
    out = out[data_window.toslices()]
    transform = blueprint.window_transform(data_window)

    print("Writing GeoTIFF...")
    outfilename = out_dir / f"indicators_{i}.tif"
    write_raster(outfilename, out, transform=transform, crs=blueprint.crs, nodata=0)

    add_overviews(outfilename)
