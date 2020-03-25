from pathlib import Path
import geopandas as gp
import pandas as pd
from geofeather import to_geofeather
from geofeather.pygeos import (
    from_geofeather as from_geofeather_as_pygeos,
    to_geofeather as to_geofeather_from_pygeos,
)
import pygeos as pg
from constants import DATA_CRS, PLANS


data_dir = Path("data")
unit_dir = data_dir / "summary_units"
boundary_dir = data_dir / "boundaries"


### Inland (HUC12) summary units
# Read in inland attributes from older version of blueprint
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

inland_atts = df


# It's already in that projection but has wrong EPSG code assigned by ArcGIS
df = (
    gp.read_file(unit_dir / "HUC12_prj.shp")[["geometry", "HUC12", "HU_12_NAME"]]
    .to_crs(DATA_CRS)
    .set_index("HUC12")
    .rename(columns={"HU_12_NAME": "name"})
)
df = df.join(inland_atts).reset_index()
# convert to bool columns if nonempty
plan_cols = df.columns.intersection(PLANS.keys())
df[plan_cols] = df[plan_cols].astype("bool")
to_geofeather(df, unit_dir / "huc12.feather")


### Marine summary units
# Read in inland attributes from older version of blueprint
cols = list(PLANS.keys()) + ["Justification"]
df = pd.read_csv(
    unit_dir / "marine_v2.csv", dtype={"PROT_NUMBE": str, "BLOCK_NUMB": str}
)
df["id"] = df.PROT_NUMBE.str.strip() + "-" + df.BLOCK_NUMB.str.strip()
df = df.set_index("id")

df = df[df.columns.intersection(cols)].copy()
for col in df.columns:
    df[col] = df[col].str.strip()


marine_atts = df

df = gp.read_file(unit_dir / "marine_blocks_prj.shp").to_crs(DATA_CRS)
df["id"] = df.PROT_NUMBE.str.strip() + "-" + df.BLOCK_NUMB.str.strip()
df = (
    df.set_index("id")[["PROT_NUMBE", "BLOCK_NUMB", "geometry"]]
    .join(marine_atts)
    .reset_index()
)
# convert to bool columns if nonempty
plan_cols = df.columns.intersection(PLANS.keys())
df[plan_cols] = df[plan_cols].fillna(False).astype("bool")
to_geofeather(df, unit_dir / "marine_blocks.feather")


### Extract the boundary
sa_df = gp.read_file(boundary_dir / "source/SALCCboundary.gdb")
to_geofeather(sa_df[["geometry"]], boundary_dir / "sa_boundary.feather")

bnd = pg.from_wkb(sa_df.geometry.apply(lambda g: g.to_wkb()))[0]


### Process TNC secured lands
print("Processing TNC secured lands...")

# This is in same projection as standard
df = gp.read_file(boundary_dir / "source/TNC_SA2018_InterimPublic.gdb")[
    ["FEE_ORGTYP", "GAP_STATUS", "geometry"]
]

# Select out areas within the SA boundary
geoms = pg.from_wkb(df.geometry.apply(lambda g: g.to_wkb()))
tree = pg.STRtree(geoms)
idx = tree.query(bnd, predicate="intersects")

df = df.iloc[idx].copy()
geoms = geoms.iloc[idx].copy()

# TODO: explode the multipolygons for better indexing (~1.1k polys)

# Fix bad geometries
# TODO: make_valid instead
fix_idx = ~pg.is_valid(geoms)
geoms[fix_idx] = pg.buffer(geoms[fix_idx], 0)
df = pd.DataFrame(df).reset_index(drop=True)
df["geometry"] = geoms
to_geofeather_from_pygeos(df, boundary_dir / "ownership.feather", crs=DATA_CRS)
