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
blueprint_filename = data_dir / "blueprint2021.tif"
corridors_filename = data_dir / "corridors.tif"
urban_filename = out_dir / "stacked_urban_30m.tif"
slr_filename = out_dir / "slr_30m.tif"
bnd_filename = data_dir / "boundaries/sa_boundary.feather"


# very small amount added to numbers to make sure that log2 gives us current number of bytes
EPS = 1e-6


# IMPORTANT: this is getting reworked so that indicator presence masks are avoided
# and where needed value ranges are shifted up by 1 value so that 0 is always NODATA


### Create groups to contain indicators and corridors up to 24 bits each
# NOTE: this is partly based on extent
groups = [
    [
        "blueprint",  # include in tiles so that we can render it after applying masks
        "corridors",  # may go away?
        "freshwater_imperiledaquaticspecies",  # 0 is meaningful, shift values up 1
        "freshwater_networkcomplexity",  # 0 = absent
        "freshwater_permeablesurface",  # 0 = absent
        "freshwater_riparianbuffers",  # 0 = absent
        "freshwater_atlanticmigratoryfishhabitat",  # 0 is meaningful, shift values up 1
        "freshwater_gulfmigratoryfishhabitat",
    ],
    # marine / coastal indicators
    [
        "land_maritimeforestextent",
        "land_beachbirds",
        "land_shorelinecondition",
        "threat_slr",
        "marine_estuarinecondition",
        "marine_fishhabitat",
        "marine_birds",
        "marine_hardbottomcoral",
    ],
    [
        "land_amphibianreptiles",
        "land_equitableparkaccess",
        "land_forestedwetlandextent",
        "land_greenways",
        "land_intactcores",
        "land_lowurbanhistoric",
        "land_marshbirds",
        "land_marshextent",
        "land_pinebirds",
    ],
    [
        "land_firefrequency",
        "land_forestbirds",
        "land_piedmontprairie",
        "land_resilientsites",
        "land_urbanparksize",
        "threat_urban",
        # spillover from others
        "marine_mammals",
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
df = pd.concat(
    [
        df,
        pd.DataFrame(
            [
                # temp, so that we can render blueprint at same resolution
                {
                    "ecosystem": "",
                    "id": "blueprint",
                    "filename": blueprint_filename,
                    "min_value": 0,
                    "max_value": 4,
                },
                {
                    "ecosystem": "",
                    "id": "corridors",
                    "filename": corridors_filename,
                    "min_value": 0,
                    "max_value": 3,
                },
                {
                    "ecosystem": "threat",
                    "id": "urban",
                    "filename": urban_filename,
                    "min_value": 0,
                    "max_value": 10,
                },
                {
                    "ecosystem": "threat",
                    "id": "slr",
                    "filename": slr_filename,
                    "min_value": 0,
                    "max_value": 6,
                },
            ]
        ),
    ]
)
df = df.set_index("id")

# any indicators that have listed 0 values need to be shifted up 1
df["value_shift"] = (df.min_value == 0).astype("uint8")
df.loc[df.value_shift == 1, "max_value"] += 1

df["bits"] = df.max_value.apply(lambda x: ceil(log2(max(x, 2) + EPS)))
df["src"] = df.filename.apply(lambda x: rasterio.open(x))
df["nodata"] = df.src.apply(lambda src: int(src.nodata))

df["group"] = 0
df["position"] = 0
id = pd.Series(df.index)
for i, ids in enumerate(groups):
    ix = df.index.isin(ids)
    df.loc[ix, "group"] = i
    df.loc[ix, "position"] = id.loc[ix].apply(lambda x: ids.index(x)).values

df = df.sort_values(by=["group", "position"])

df["offset"] = 0

# calculate bit offsets for each entity within each group
for group in df.group.unique():
    df.loc[df.group == group, "offset"] = (
        np.cumsum(df.loc[df.group == group].bits) - df.loc[df.group == group].bits
    )

for col in ["group", "position", "bits", "offset", "min_value", "max_value"]:
    df[col] = df[col].astype("uint8")

# NOTE: groups must be stored in encoding definition
# in exactly the same order they are encoded
df[["group", "position", "offset", "bits", "value_shift"]].reset_index().to_feather(
    out_dir / "encoding.feather"
)

# save encoding JSON for frontend
for group in sorted(df.group.unique()):
    with open(out_dir / f"indicators_{group}.json", "w") as out:
        out.write(
            df.loc[df.group == group, ["position", "offset", "bits", "value_shift"]]
            .rename(columns={"value_shift": "valueShift"})
            .reset_index()
            .to_json(orient="records")
        )


group_bits = df.groupby("group").bits.sum()

print("Planned bits per group")
print(group_bits)

if group_bits.max() > 24:
    raise ValueError("Group bits must be <= 24")


### determine the block windows that overlap bounds
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
    total_bits = rows.bits.sum()

    # Find least number of bands that will hold the encoded data
    if total_bits <= 8:
        dtype = "uint8"
        num_bytes = 1

    elif total_bits <= 16:
        dtype = "uint16"
        num_bytes = 2

    else:
        dtype = "uint32"
        num_bytes = 4

    out = np.zeros(shape=blueprint.shape, dtype=dtype)

    # windows = windows[957:958] # example window with data

    for window in Bar(
        f"Processing group {i} ({total_bits} bits)", max=len(windows)
    ).iter(windows):
        window_shape = (window.height, window.width)
        ix = window.toslices()
        has_data = False
        layer_bits = []
        for id in rows.index:
            row = rows.loc[id]

            data = row.src.read(1, window=window)

            # shift values up if needed
            if row.value_shift:
                data[data != row.nodata] += 1

            # set nodata pixels to 0 (combined with existing 0 values that are below row.min_value)
            data[data == row.nodata] = 0

            if data.max() > 0:
                out[ix] = np.bitwise_or(
                    np.left_shift(data.astype("uint32"), row.offset), out[ix]
                )

    # determine the window where data are available, and write out a smaller output
    print("Calculating data window...")
    data_window = get_data_window(out, nodata=0)
    out = out[data_window.toslices()]
    transform = blueprint.window_transform(data_window)

    print("Writing GeoTIFF...")
    outfilename = out_dir / f"indicators_{i}.tif"
    write_raster(outfilename, out, transform=transform, crs=blueprint.crs, nodata=0)

    add_overviews(outfilename)


#### Notes
# to verify that values are encoded correctly
# 1. cast encoded values to correct type (e.g., uint16): value = encoded[106,107].view('uint16')
# 2. use bit shifting and bit AND logic to extract value, based on offset and nbits:
# (value >> offset) & ((2**nbits)-1) # => original value
