from pathlib import Path
import pandas as pd
import pygeos as pg
import geopandas as gp
from geofeather import from_geofeather, to_geofeather
from geofeather.pygeos import to_geofeather as to_geofeather_from_pygeos

from util.pygeos_util import to_pygeos, from_pygeos, sjoin, to_crs
from constants import GEO_CRS, DATA_CRS

### Consolidate HUC12 and marine blocks and output as geojson
working_dir = Path("data/summary_units")

huc12 = from_geofeather(working_dir / "huc12_prj.feather")[
    ["HUC12", "geometry"]
].rename(columns={"HUC12": "id"})
marine = from_geofeather(working_dir / "marine_blocks_prj.feather")[["id", "geometry"]]

# TODO: simplify (slightly): try to get rid of overlaps between units

# Create consolidated summary units file as WGS84
df = (
    huc12.append(marine, ignore_index=True, sort=False)
    .reset_index(drop=True)
    .to_crs(GEO_CRS)
)
to_geofeather(df, working_dir / "units.feather")


# Create GeoJSONSeq file for vector tiles
df.to_file(working_dir / "units.geojson", driver="GeoJSONSeq")


### Create mask by cutting SA bounds out of arbitrarily large polygon
working_dir = Path("data/boundaries")
sa_bnd = gp.read_file(working_dir / "source/SALCCboundary.gdb", layer="SALCC_ACF")[
    ["geometry"]
].to_crs(GEO_CRS)
sa_bnd = to_pygeos(sa_bnd.geometry)

# Clip boundary from outer box
outer = pg.box(-180, -85, 180, 85)
mask = pg.difference(outer, sa_bnd)

mask = from_pygeos(mask)

df = gp.GeoDataFrame({"geometry": mask}, crs=GEO_CRS)
df.to_file(working_dir / "mask.geojson", driver="GeoJSONSeq")


### Extract counties within SA bounds
states = (
    gp.read_file(working_dir / "source/tl_2019_us_state.shp")[["STATEFP", "NAME"]]
    .rename(columns={"NAME": "state"})
    .set_index("STATEFP")
)

# coordinates are in geographic coordinates (NAD83 vs WGS84)
df = gp.read_file(working_dir / "source/tl_2018_us_county.shp")
crs = df.crs
df = pd.DataFrame(df.copy())
df["geometry"] = to_pygeos(df.geometry)

in_bnd = sjoin(df, pd.DataFrame({"geometry": sa_bnd}), how="inner")

df = (
    in_bnd[["STATEFP", "GEOID", "NAME", "geometry"]]
    .rename(columns={"GEOID": "FIPS", "NAME": "county"})
    .join(states, on="STATEFP")
)
df = df[["FIPS", "state", "county", "geometry"]].reset_index(drop=True)

df["geometry"] = to_crs(df.geometry, crs, DATA_CRS)

to_geofeather_from_pygeos(df, working_dir / "counties.feather", crs=DATA_CRS)

df["geometry"] = from_pygeos(df.geometry)

df = gp.GeoDataFrame(df, crs=DATA_CRS)
df.to_file("/tmp/counties.shp")
