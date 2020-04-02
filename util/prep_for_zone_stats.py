from pathlib import Path
import geopandas as gp
import pandas as pd
from geofeather import to_geofeather
from geofeather.pygeos import (
    from_geofeather as from_geofeather_as_pygeos,
    to_geofeather as to_geofeather_from_pygeos,
)
import pygeos as pg

from constants import DATA_CRS, GEO_CRS, PLANS
from util.pygeos_util import to_pygeos

data_dir = Path("data")
unit_dir = data_dir / "summary_units"
out_dir = data_dir / "derived"
boundary_dir = data_dir / "boundaries"


### Inland (HUC12) summary units

# It's already in that projection but has wrong EPSG code assigned by ArcGIS
print("Reading HUC12...")
huc12 = (
    gp.read_file(unit_dir / "HUC12_prj.shp")[["geometry", "HUC12", "HU_12_NAME"]]
    .to_crs(DATA_CRS)
    .set_index("HUC12")
    .rename(columns={"HU_12_NAME": "name"})
)

# save for analysis
to_geofeather(huc12[["geometry"]].reset_index(), unit_dir / "huc12_prj.feather")

# calculate area
huc12["acres"] = huc12.area * 0.000247105

# reproject to WGS84
huc12 = huc12.to_crs(GEO_CRS)


# Read in inland attributes from older version of blueprint
print("Reading HUC12 attributes...")
cols = list(PLANS.keys()) + ["Justification"]
df = pd.read_csv(
    unit_dir / "JustifiationCleanUp2017_InlandBlueprint_1_0_07Sept2014.csv",
    dtype={"HUC12": str},
).set_index("HUC12")

df = df[df.columns.intersection(cols)].copy()
for col in df.columns:
    df[col] = df[col].str.strip()

df["Justification"] = (
    df.Justification.str.replace("[", "")
    .str.replace("]", "")
    .str.replace(" ... ", ". ")
)

huc12 = huc12.join(df)
# convert to bool columns if nonempty
plan_cols = huc12.columns.intersection(PLANS.keys())
huc12[plan_cols] = huc12[plan_cols].astype("bool")

to_geofeather(huc12.reset_index(), out_dir / "huc12" / "huc12.feather")


### Marine summary units
print("Reading marine blocks...")
df = gp.read_file(unit_dir / "marine_blocks_prj.shp").to_crs(DATA_CRS)
df["id"] = df.PROT_NUMBE.str.strip() + "-" + df.BLOCK_NUMB.str.strip()
df = df.set_index("id")[["PROT_NUMBE", "BLOCK_NUMB", "geometry"]]

# save for analysis
to_geofeather(df[["geometry"]].reset_index(), unit_dir / "marine_blocks_prj.feather")

# calculate area
df["acres"] = df.area * 0.000247105

# reproject to WGS84
df = df.to_crs(GEO_CRS)
marine = df

# Read in inland attributes from older version of blueprint
print("Reading marine attributes...")
cols = ["name"] + list(PLANS.keys()) + ["Justification"]
df = pd.read_csv(
    unit_dir / "marine_v2.csv", dtype={"PROT_NUMBE": str, "BLOCK_NUMB": str}
)
df["id"] = df.PROT_NUMBE.str.strip() + "-" + df.BLOCK_NUMB.str.strip()
df = df.set_index("id")

df["name"] = df.PROT_NUMBE.str.strip() + ": Block " + df.BLOCK_NUMB.str.strip()


df = df[df.columns.intersection(cols)].copy()
for col in df.columns:
    df[col] = df[col].str.strip()

marine = marine.join(df)

# convert to bool columns if nonempty
plan_cols = marine.columns.intersection(PLANS.keys())
marine[plan_cols] = marine[plan_cols].fillna(False).astype("bool")
to_geofeather(marine.reset_index(), out_dir / "marine_blocks" / "marine_blocks.feather")


### Extract the boundary
sa_df = gp.read_file(boundary_dir / "source/SALCCboundary.gdb")
to_geofeather(sa_df[["geometry"]], boundary_dir / "sa_boundary.feather")

bnd = to_pygeos(sa_df.geometry)[0]

### Process TNC secured lands
print("Processing TNC secured lands...")

# This is in same projection as standard
df = gp.read_file(boundary_dir / "source/TNC_SA2018_InterimPublic.gdb")[
    ["FEE_ORGTYP", "GAP_STATUS", "geometry"]
]

# Select out areas within the SA boundary
geoms = to_pygeos(df.geometry)
tree = pg.STRtree(geoms)
idx = tree.query(bnd, predicate="intersects")

df = pd.DataFrame(df.iloc[idx].drop(columns=["geometry"]))

geoms = geoms[idx].copy()

# TODO: explode the multipolygons for better indexing (~1.1k polys)

# Fix bad geometries
# TODO: make_valid instead
fix_idx = ~pg.is_valid(geoms)
geoms[fix_idx] = pg.buffer(geoms[fix_idx], 0)
df["geometry"] = geoms
to_geofeather_from_pygeos(
    df.reset_index(), boundary_dir / "ownership.feather", crs=DATA_CRS
)
