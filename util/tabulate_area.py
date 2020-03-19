import csv
import os
from pathlib import Path
from time import time
import warnings

import pandas as pd
import geopandas as gp

# from geofeather.pygeos import from_geofeather
from geofeather import from_geofeather
from geofeather.pygeos import from_geofeather as from_geofeather_as_pygeos
import numpy as np
from progress.bar import Bar
import pygeos as pg
import rasterio
from rasterio.mask import raster_geometry_mask

from util.io import write_raster
from constants import BLUEPRINT, INDICATORS, URBAN_YEARS
from stats import (
    extract_count_in_geometry,
    extract_blueprint_indicator_counts,
    extract_urbanization_counts,
    extract_slr_counts,
)


data_dir = Path("data")
out_dir = data_dir / "derived/huc12"
huc12_filename = data_dir / "summary_units/HUC12.feather"

if not out_dir.exists():
    os.makedirs(out_dir)

start = time()

# TODO: pygeos version and map to __geo_interface__
print("Reading HUC12 boundaries")
geometries = from_geofeather(huc12_filename, columns=["geometry"]).geometry

### Calculate counts of each category in blueprint and indicators and put into a DataFrame
results = []
for i, geometry in Bar(
    "Calculating Blueprint and Indicator counts for HUC12", max=len(geometries)
).iter(geometries.iteritems()):
    counts = extract_blueprint_indicator_counts([geometry], inland=True)
    if counts is None:
        continue

    results.append(counts)

df = pd.DataFrame(results)
df["id"] = df.index.copy()
df.id = df.id.astype("uint16")  # TODO: double check count of marine

### Export the Blueprint and each indicator to a separate file
# each column is an array of counts for each
for col in df.columns.difference(["id", "mask"]):
    s = df[col].apply(pd.Series)
    # add mask column
    s["mask"] = df["mask"]

    max_count = s.max().max()
    if max_count <= 255:
        s = s.astype("uint8")
    elif max_count <= 65535:
        s = s.astype("uint16")
    else:
        s = s.astype("uint32")

    s["id"] = df["id"]  # preserve index values
    # drop rows that do not have this indicator present
    s = s.loc[s.sum(axis=1) > 0].reset_index(drop=True)
    if not len(s):
        warnings.warn(
            f"Indicator does not have any data present anywhere in region: {col}"
        )
        continue

    # order columns
    s = s[["id", "mask"] + list(s.columns.difference(["id", "mask"]))]
    s.columns = [str(c) for c in s.columns]
    s.to_feather(out_dir / f"{col}.feather")
    s.to_csv(out_dir / f"{col}.csv", index=False)

### Calculate counts for urbanization
results = []
for i, geometry in Bar(
    "Calculating Urbanization counts for HUC12", max=len(geometries)
).iter(geometries.iteritems()):
    counts = extract_urbanization_counts([geometry])
    if counts is None:
        continue

    results.append(counts)


cols = ["mask"] + URBAN_YEARS
df = pd.DataFrame(results)[cols]

max_count = df.max().max()
if max_count < 65535:
    df = df.astype("uint16")
else:
    df = df.astype("uint32")

df["id"] = df.index.copy()
df.id = df.id.astype("uint16")
df.columns = [str(c) for c in df.columns]
df.to_feather(out_dir / "urban.feather")
df.to_csv(out_dir / "urban.csv", index=False)


### Calculate counts for SLR

bounds = from_geofeather_as_pygeos(data_dir / "threats/slr/slr_bounds.feather")
tree = pg.STRtree(bounds.geometry)

# convert to pygeos geometries; there are some invalid data, so buffer them by 0
geoms = pg.buffer(pg.from_shapely(geometries.geometry), 0)

# find the indexes of the geometries that overlap with SLR bounds; these are the only
# ones that need to be analyzed for SLR impacts
slr_geom_idx = np.unique(tree.query_bulk(geoms, predicate="intersects")[0])

slr_geometries = pd.DataFrame(geometries.copy())

# add in original index
slr_geometries["id"] = slr_geometries.index.copy()
slr_geometries.id = slr_geometries.id.astype("uint16")

slr_geometries = slr_geometries.loc[slr_geom_idx]

results = []
ids = []
for i, row in Bar("Calculating SLR counts for HUC12", max=len(slr_geometries)).iter(
    slr_geometries.iterrows()
):
    counts = extract_slr_counts([row.geometry])
    if counts is None:
        continue

    ids.append(row.id)
    results.append(counts)

df = pd.DataFrame(results)
df["id"] = np.array(ids, dtype="uint16")
# reorder columns
df = df[["id", "mask"] + list(df.columns.difference(["id", "mask"]))]
# extract only areas that actually had SLR pixels
df = df[df[df.columns[2:]].sum(axis=1) > 0].reset_index(drop=True)

for col in df.columns[1:]:
    dtype = "uint64"

    if df[col].max() < 4294967295:
        dtype = "uint32"

    df[col] = df[col].astype(dtype)

df.columns = [str(c) for c in df.columns]
df.to_feather(out_dir / "slr.feather")
df.to_csv(out_dir / "slr.csv", index=False)


print(
    "Processed {:,} zones in {:.2f}m".format(len(geometries), (time() - start) / 60.0)
)

