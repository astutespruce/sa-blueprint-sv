from pathlib import Path
import pandas as pd
import geopandas as gp
import pygeos as pg
from pyogrio.geopandas import read_dataframe, write_dataframe
from geofeather import from_geofeather as from_geofeather_as_gp

from analysis.constants import GEO_CRS, DATA_CRS
from analysis.pygeos_util import explode


src_dir = Path("source_data")
data_dir = Path("data")
out_dir = data_dir / "inputs/boundaries"  # used as inputs for other steps
bnd_dir = data_dir / "boundaries"  # used as inputs for tiles


sa_df = read_dataframe(src_dir / "boundaries/SABlueprint2020_ExtentP.shp")

### Create mask by cutting SA bounds out of world bounds
print("Creating mask...")
world = pg.box(-180, -85, 180, 85)
bnd = sa_df.to_crs(GEO_CRS).geometry.values.data
mask = pg.normalize(pg.difference(world, bnd))

# DEBUG
# write_dataframe(
#     gp.GeoDataFrame({"geometry": bnd}, index=[0], crs=GEO_CRS),
#     bnd_dir / "sa_bnd.gpkg",
#     driver="GPKG",
# )


write_dataframe(
    gp.GeoDataFrame({"geometry": mask}, index=[0], crs=GEO_CRS),
    bnd_dir / "sa_mask.gpkg",
    driver="GPKG",
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
ix = tree.query(sa_df.geometry.values.data[0], predicate="intersects")
counties = counties.iloc[ix].join(states, on="STATEFP").drop(columns=["STATEFP"])


# write_dataframe(counties, out_dir / "counties.gpkg", driver="GPKG")
counties.to_feather(out_dir / "counties.feather")


### Protected areas (TNC secured lands)
print("Processing TNC secured lands...")

# already in EPSG:5070
df = read_dataframe(
    src_dir / "boundaries/TNC_SA2018_InterimPublic.gdb",
    columns=["FEE_ORGTYP", "GAP_STATUS"],
)

tree = pg.STRtree(df.geometry.values.data)
ix = tree.query(sa_df.geometry.values.data[0], predicate="intersects")
df = df.iloc[ix].copy()

# make sure geometries are valid
df["geometry"] = pg.make_valid(df.geometry.values.data)

# Explode the polygons for better spatial index results in downstream functions
df = explode(df)

write_dataframe(df, bnd_dir / "ownership.gpkg", driver="GPKG")
df.to_feather(out_dir / "ownership.feather")
