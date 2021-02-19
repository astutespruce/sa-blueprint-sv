from pathlib import Path
import pandas as pd
import geopandas as gp
import pygeos as pg
from pyogrio.geopandas import read_dataframe, write_dataframe

# suppress warnings abuot writing to feather
import warnings

warnings.filterwarnings("ignore", message=".*initial implementation of Parquet.*")

from analysis.constants import GEO_CRS, DATA_CRS
from analysis.lib.pygeos_util import explode


src_dir = Path("source_data")
data_dir = Path("data")
out_dir = data_dir / "inputs/boundaries"  # used as inputs for other steps
tile_dir = data_dir / "for_tiles"


sa_df = read_dataframe(src_dir / "boundaries/SABlueprint2020_Extent.shp")

### Create mask by cutting SA bounds out of world bounds
print("Creating mask...")
world = pg.box(-180, -85, 180, 85)

# boundary has self-intersections and 4 geometries, need to clean up

bnd = pg.union_all(pg.make_valid(sa_df.geometry.values.data))
bnd_geo = pg.union_all(pg.make_valid(sa_df.to_crs(GEO_CRS).geometry.values.data))
mask = pg.normalize(pg.difference(world, bnd_geo))

gp.GeoDataFrame(geometry=[bnd], crs=DATA_CRS).to_feather(
    out_dir / "sa_boundary.feather"
)

write_dataframe(
    gp.GeoDataFrame({"geometry": bnd_geo}, index=[0], crs=GEO_CRS),
    tile_dir / "sa_boundary.geojson",
    driver="GeoJSONSeq",
)

write_dataframe(
    gp.GeoDataFrame({"geometry": mask}, index=[0], crs=GEO_CRS),
    tile_dir / "sa_mask.geojson",
    driver="GeoJSONSeq",
)

### Extract counties within SA bounds
print("Extracting states and counties...")
states = (
    read_dataframe(
        src_dir / "boundaries/tl_2019_us_state.shp",
        read_geometry=False,
        columns=["STATEFP", "NAME"],
    )
    .rename(columns={"NAME": "state"})
    .set_index("STATEFP")
)

counties = (
    read_dataframe(
        src_dir / "boundaries/tl_2018_us_county.shp",
        columns=["STATEFP", "GEOID", "NAME", "geometry"],
    )
    .rename(columns={"GEOID": "FIPS", "NAME": "county"})
    .to_crs(DATA_CRS)
)

# select counties within the SA boundary
tree = pg.STRtree(counties.geometry.values.data)
ix = tree.query(bnd, predicate="intersects")
counties = counties.iloc[ix].join(states, on="STATEFP").drop(columns=["STATEFP"])


# write_dataframe(counties, out_dir / "counties.gpkg", driver="GPKG")
counties.to_feather(out_dir / "counties.feather")


### Protected areas (TNC secured lands)
print("Processing TNC secured lands...")

# already in EPSG:5070
df = read_dataframe(
    src_dir / "boundaries/TNC_SA2018_InterimPublic.gdb",
    columns=["FEE_ORGTYP", "GAP_STATUS", "AREA_NAME", "FEE_OWNER"],
)

tree = pg.STRtree(df.geometry.values.data)
ix = tree.query(bnd, predicate="intersects")
df = df.iloc[ix].copy()

# make sure geometries are valid
df["geometry"] = pg.make_valid(df.geometry.values.data)

# Explode the polygons for better spatial index results in downstream functions
df = explode(df).reset_index(drop=True)

write_dataframe(df.to_crs(GEO_CRS), tile_dir / "ownership.geojson", driver="GeoJSONSeq")
df.to_feather(out_dir / "ownership.feather")


### PARCAs (Amphibian & reptile aras)
# already in EPSG:5070
print("Processing PARCAs...")
df = read_dataframe(
    src_dir / "boundaries/SouthAtlanticPARCAs.gdb",
    columns=["FID", "Name", "Description"],
    force_2d=True,
).rename(columns={"FID": "parca_id", "Name": "name", "Description": "description"})

df = explode(df).reset_index(drop=True)
tree = pg.STRtree(df.geometry.values.data)
ix = tree.query(bnd, predicate="intersects")
df = df.iloc[ix].copy()

df.geometry = pg.make_valid(df.geometry.values.data)

df.to_feather(out_dir / "parca.feather")

