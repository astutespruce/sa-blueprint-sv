import csv
import os
from pathlib import Path
from time import time
import warnings

import pandas as pd
import geopandas as gp

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


def get_minimum_type(max_value):
    if max_value <= 255:
        return "uint8"
    if max_value <= 65535:
        return "uint16"
    if max_value <= 4294967295:
        return "uint32"
    return "uint64"


data_dir = Path("data")
huc12_filename = data_dir / "summary_units/HUC12.feather"
marine_filename = data_dir / "summary_units/marine_blocks.feather"
ownership_filename = data_dir / "boundaries/ownership.feather"

start = time()


# ### Inland
out_dir = data_dir / "derived/huc12"
if not out_dir.exists():
    os.makedirs(out_dir)

# TODO: pygeos version and map to __geo_interface__
print("Reading HUC12 boundaries")
geometries = (
    from_geofeather(huc12_filename, columns=["HUC12", "geometry"])
    .set_index("HUC12")
    .geometry
)


### Calculate counts of each category in blueprint and indicators and put into a DataFrame
results = []
index = []
for huc12, geometry in Bar(
    "Calculating Blueprint and Indicator counts for HUC12", max=len(geometries)
).iter(geometries.iteritems()):
    counts = extract_blueprint_indicator_counts([geometry], inland=True)
    if counts is None:
        continue

    index.append(huc12)
    results.append(counts)

df = pd.DataFrame(results, index=index)
df["shape_mask"] = df.shape_mask.astype(get_minimum_type(df.shape_mask.max()))

### Export the Blueprint and each indicator to a separate file
# each column is an array of counts for each
for col in df.columns.difference(["shape_mask"]):
    s = df[col].apply(pd.Series)

    # drop rows that do not have this indicator present
    s = s.loc[s.sum(axis=1) > 0].copy()
    if not len(s):
        warnings.warn(
            f"Indicator does not have any data present anywhere in region: {col}"
        )
        continue

    # cast to smallest types
    for c in s.columns:
        s[c] = s[c].astype(get_minimum_type(s[c].max()))

    # add mask column
    s = s.join(df.shape_mask)

    # order columns
    s = (
        s[["shape_mask"] + list(s.columns.difference(["shape_mask"]))]
        .reset_index()
        .rename(columns={"index": "huc12"})
    )
    s.columns = [str(c) for c in s.columns]
    s.to_feather(out_dir / f"{col}.feather")
    s.to_csv(out_dir / f"{col}.csv", index=False)

### Calculate counts for urbanization
index = []
results = []
for huc12, geometry in Bar(
    "Calculating Urbanization counts for HUC12", max=len(geometries)
).iter(geometries.iteritems()):
    counts = extract_urbanization_counts([geometry])
    if counts is None:
        continue

    index.append(huc12)
    results.append(counts)

cols = ["shape_mask"] + URBAN_YEARS
df = pd.DataFrame(results, index=index)[cols]
for col in df.columns:
    df[col] = df[col].astype(get_minimum_type(df[col].max()))

df = df.reset_index().rename(columns={"index": "huc12"})
df.columns = [str(c) for c in df.columns]
df.to_feather(out_dir / "urban.feather")
df.to_csv(out_dir / "urban.csv", index=False)


### Calculate counts for SLR

bounds = from_geofeather_as_pygeos(data_dir / "threats/slr/slr_bounds.feather")
tree = pg.STRtree(bounds.geometry)

# convert to pygeos geometries; there are some invalid data, so buffer them by 0
geoms = pg.buffer(pg.from_shapely(geometries.geometry), 0)

slr_geometries = geometries.copy()
# find the indexes of the geometries that overlap with SLR bounds; these are the only
# ones that need to be analyzed for SLR impacts
slr_geom_idx = np.unique(tree.query_bulk(geoms, predicate="intersects")[0])
slr_geometries = slr_geometries.iloc[slr_geom_idx]

results = []
index = []
for huc12, geometry in Bar(
    "Calculating SLR counts for HUC12", max=len(slr_geometries)
).iter(slr_geometries.iteritems()):
    counts = extract_slr_counts([geometry])
    if counts is None:
        continue

    index.append(huc12)
    results.append(counts)

df = pd.DataFrame(results, index=index)

# reorder columns
df = df[["shape_mask"] + list(df.columns.difference(["shape_mask"]))]
# extract only areas that actually had SLR pixels
df = df[df[df.columns[1:]].sum(axis=1) > 0]

for col in df.columns[1:]:
    df[col] = df[col].astype(get_minimum_type(df[col].max()))

df.columns = [str(c) for c in df.columns]
df = df.reset_index().rename(columns={"index": "huc12"})
df.to_feather(out_dir / "slr.feather")
df.to_csv(out_dir / "slr.csv", index=False)


### Calculate overlap with ownership and protection
print("Calculating overlap with land ownership and protection")
geometries = (
    from_geofeather_as_pygeos(huc12_filename, columns=["HUC12", "geometry"]).set_index(
        "HUC12"
    )
)[["geometry"]]

df = from_geofeather_as_pygeos(ownership_filename)

# create and query tree for join
tree = pg.STRtree(df.geometry)
left_idx, right_idx = tree.query_bulk(geometries.geometry, predicate="intersects")
right = pd.DataFrame(
    df.iloc[right_idx].index.values,
    index=geometries.iloc[left_idx].index.values,
    columns=["index_right"],
).join(df, on="index_right")
joined = geometries.join(right, how="inner", rsuffix="_right")
joined["acres"] = (
    pg.area(pg.intersection(joined.geometry, joined.geometry_right)) * 0.000247105
)

by_owner = (
    joined[["FEE_ORGTYP", "acres"]]
    .groupby(by=[joined.index.get_level_values(0), "FEE_ORGTYP"])
    .acres.sum()
    .astype("float32")
    .reset_index()
    .rename(columns={"level_0": "HUC12"})
)
by_owner.to_feather(out_dir / "ownership.feather")
by_owner.to_csv(out_dir / "ownership.csv", index=False)

by_protection = (
    joined[["GAP_STATUS", "acres"]]
    .groupby(by=[joined.index.get_level_values(0), "GAP_STATUS"])
    .acres.sum()
    .astype("float32")
    .reset_index()
    .rename(columns={"level_0": "HUC12"})
)
by_protection.to_feather(out_dir / "protection.feather")
by_protection.to_csv(out_dir / "protection.csv", index=False)

### Marine blocks
out_dir = data_dir / "derived/marine"
if not out_dir.exists():
    os.makedirs(out_dir)

print("Reading marine blocks boundaries")
df = from_geofeather(marine_filename, columns=["id", "geometry"]).set_index("id")

### Calculate counts of each category in blueprint and indicators and put into a DataFrame
results = []
index = []
for id, geometry in Bar(
    "Calculating Blueprint and Indicator counts for marine blocks", max=len(geometries)
).iter(geometries.iteritems()):
    counts = extract_blueprint_indicator_counts([geometry], inland=False)
    if counts is None:
        continue

    index.append(id)
    results.append(counts)

df = pd.DataFrame(results, index=index)
df["shape_mask"] = df.shape_mask.astype(get_minimum_type(df.shape_mask.max()))

### Export the Blueprint and each indicator to a separate file
# each column is an array of counts for each
for col in df.columns.difference(["shape_mask"]):
    s = df[col].apply(pd.Series)

    # drop rows that do not have this indicator present
    s = s.loc[s.sum(axis=1) > 0].copy()
    if not len(s):
        warnings.warn(
            f"Indicator does not have any data present anywhere in region: {col}"
        )
        continue

    # cast to smallest types
    for c in s.columns:
        s[c] = s[c].astype(get_minimum_type(s[c].max()))

    # add mask column
    s = s.join(df.shape_mask)

    # order columns
    s = (
        s[["shape_mask"] + list(s.columns.difference(["shape_mask"]))]
        .reset_index()
        .rename(columns={"index": "id"})
    )
    s.columns = [str(c) for c in s.columns]
    s.to_feather(out_dir / f"{col}.feather")
    s.to_csv(out_dir / f"{col}.csv", index=False)


print(
    "Processed {:,} zones in {:.2f}m".format(len(geometries), (time() - start) / 60.0)
)
