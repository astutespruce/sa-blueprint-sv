import csv
import os
from pathlib import Path
from time import time
import warnings

import pandas as pd
import geopandas as gp

from geofeather.pygeos import from_geofeather, to_geofeather
import numpy as np
from progress.bar import Bar
import pygeos as pg
import rasterio
from rasterio.mask import raster_geometry_mask

from util.io import write_raster
from util.pygeos_util import (
    to_crs,
    to_pygeos,
    sjoin,
    to_dict,
    sjoin_geometry,
    intersection,
)
from constants import BLUEPRINT, INDICATORS, URBAN_YEARS, DATA_CRS, GEO_CRS, M2_ACRES
from stats import (
    extract_count_in_geometry,
    extract_blueprint_indicator_area,
    extract_urbanization_area,
    extract_slr_area,
)


data_dir = Path("data")
huc12_filename = data_dir / "summary_units/HUC12.feather"
marine_filename = data_dir / "summary_units/marine_blocks.feather"
ownership_filename = data_dir / "boundaries/ownership.feather"
county_filename = data_dir / "boundaries/counties.feather"
slr_bounds_filename = data_dir / "threats/slr/slr_bounds.feather"

start = time()


### Inland
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
    zone_results = extract_blueprint_indicator_area([to_dict(geometry)], inland=True)
    if zone_results is None:
        continue

    index.append(huc12)
    results.append(zone_results)

df = pd.DataFrame(results, index=index)
results = df[["shape_mask"]].copy()

### Export the Blueprint and each indicator to a separate file
# each column is an array of counts for each
for col in df.columns.difference(["shape_mask"]):
    s = df[col].apply(pd.Series)
    s.columns = [f"{col}_{c}" for c in s.columns]
    results = results.join(s)

results.index.name = "HUC12"
results.to_csv(out_dir / "blueprint_results.csv", index_label="HUC12")
results.reset_index().to_feather(out_dir / "blueprint_results.feather")


### Calculate counts for urbanization
index = []
results = []
for huc12, geometry in Bar(
    "Calculating Urbanization counts for HUC12", max=len(geometries)
).iter(geometries.iteritems()):
    zone_results = extract_urbanization_area([to_dict(geometry)])
    if zone_results is None:
        continue

    index.append(huc12)
    results.append(zone_results)

cols = ["shape_mask"] + URBAN_YEARS
df = pd.DataFrame(results, index=index)[cols]
df = df.reset_index().rename(columns={"index": "HUC12"})
df.columns = [str(c) for c in df.columns]
df.to_feather(out_dir / "urban.feather")
df.to_csv(out_dir / "urban.csv", index=False)


### Calculate counts for SLR
# find the indexes of the geometries that overlap with SLR bounds; these are the only
# ones that need to be analyzed for SLR impacts
slr_bounds = from_geofeather(slr_bounds_filename).geometry
idx = sjoin_geometry(geometries, slr_bounds.values, how="inner")
slr_geometries = geometries.iloc[idx]

results = []
index = []
for huc12, geometry in Bar(
    "Calculating SLR counts for HUC12", max=len(slr_geometries)
).iter(slr_geometries.iteritems()):
    zone_results = extract_slr_area([to_dict(geometry)])
    if zone_results is None:
        continue

    index.append(huc12)
    results.append(zone_results)

df = pd.DataFrame(results, index=index)

# reorder columns
df = df[["shape_mask"] + list(df.columns.difference(["shape_mask"]))]
# extract only areas that actually had SLR pixels
df = df[df[df.columns[1:]].sum(axis=1) > 0]
df.columns = [str(c) for c in df.columns]
df = df.reset_index().rename(columns={"index": "HUC12"})
df.to_feather(out_dir / "slr.feather")
df.to_csv(out_dir / "slr.csv", index=False)


### Calculate overlap with ownership and protection
print("Calculating overlap with land ownership and protection")
ownership = from_geofeather(
    ownership_filename, columns=["geometry", "FEE_ORGTYP", "GAP_STATUS"]
)

df = intersection(pd.DataFrame({"geometry": geometries}), ownership)
df["acres"] = pg.area(df.geometry_right) * M2_ACRES

# drop areas that touch but have no overlap
df = df.loc[df.acres > 0].copy()

by_owner = (
    df[["FEE_ORGTYP", "acres"]]
    .groupby(by=[df.index.get_level_values(0), "FEE_ORGTYP"])
    .acres.sum()
    .astype("float32")
    .reset_index()
    .rename(columns={"level_0": "HUC12"})
)
by_owner.to_feather(out_dir / "ownership.feather")
by_owner.to_csv(out_dir / "ownership.csv", index=False)

by_protection = (
    df[["GAP_STATUS", "acres"]]
    .groupby(by=[df.index.get_level_values(0), "GAP_STATUS"])
    .acres.sum()
    .astype("float32")
    .reset_index()
    .rename(columns={"level_0": "HUC12"})
)
by_protection.to_feather(out_dir / "protection.feather")
by_protection.to_csv(out_dir / "protection.csv", index=False)

### Calculate spatial join with counties
print("Calculating spatial join with counties")
df = from_geofeather(county_filename)
df = sjoin(
    pd.DataFrame({"geometry": geometries}, index=geometries.index), df, how="inner"
)[["FIPS", "state", "county"]].reset_index()
df.to_feather(out_dir / "counties.feather")
df.to_csv(out_dir / "counties.csv", index=False)


# ##########################################################################


### Marine blocks
out_dir = data_dir / "derived/marine_blocks"
if not out_dir.exists():
    os.makedirs(out_dir)

print("Reading marine blocks boundaries")
df = from_geofeather(marine_filename, columns=["id", "geometry"]).set_index("id")
geometries = df.geometry

### Calculate counts of each category in blueprint and indicators and put into a DataFrame
results = []
index = []
for id, geometry in Bar(
    "Calculating Blueprint and Indicator counts for marine blocks", max=len(geometries)
).iter(geometries.iteritems()):
    zone_results = extract_blueprint_indicator_area([to_dict(geometry)], inland=False)
    if zone_results is None:
        continue

    index.append(id)
    results.append(zone_results)

df = pd.DataFrame(results, index=index)
results = df[["shape_mask"]].copy()

### Export the Blueprint and each indicator to a separate file
# each column is an array of counts for each
for col in df.columns.difference(["shape_mask"]):
    s = df[col].apply(pd.Series)
    s.columns = [f"{col}_{c}" for c in s.columns]
    results = results.join(s)

results.index.name = "id"
results.to_csv(out_dir / "blueprint.csv", index_label="id")
results.reset_index().to_feather(out_dir / "blueprint.feather")

print(
    "Processed {:,} zones in {:.2f}m".format(len(geometries), (time() - start) / 60.0)
)
