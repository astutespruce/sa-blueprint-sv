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
out_dir = data_dir / "derived/huc12"
huc12_filename = data_dir / "summary_units/HUC12.feather"

if not out_dir.exists():
    os.makedirs(out_dir)

start = time()

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
for col in df.columns.difference(["id", "shape_mask"]):
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
        s[["shape_mask"] + list(s.columns.difference(["id", "shape_mask"]))]
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


print(
    "Processed {:,} zones in {:.2f}m".format(len(geometries), (time() - start) / 60.0)
)
