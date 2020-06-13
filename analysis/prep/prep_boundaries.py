from pathlib import Path
import pandas as pd
import geopandas as gp
import pygeos as pg
import pyogrio as pio
from pyogrio.geopandas import write_dataframe
from geofeather.pygeos import from_geofeather, to_geofeather
from geofeather import from_geofeather as from_geofeather_as_gp

from analysis.constants import GEO_CRS, DATA_CRS
from analysis.pygeos_util import to_pygeos, from_pygeos, sjoin, to_crs


### Consolidate HUC12 and marine blocks and output as geojson
src_dir = Path("source_data/summary_units")
out_dir = Path("data/summary_units")

huc12 = from_geofeather(out_dir / "huc12_prj.feather")[["HUC12", "geometry"]].rename(
    columns={"HUC12": "id"}
)
marine = from_geofeather(out_dir / "marine_blocks_prj.feather")[["id", "geometry"]]

# TODO: simplify (slightly): try to get rid of overlaps between units

# Create consolidated summary units file as WGS84
df = huc12.append(marine, ignore_index=True, sort=False).reset_index(drop=True)
df.geometry = to_crs(df.geometry, DATA_CRS, GEO_CRS)
to_geofeather(df, out_dir / "units.feather", crs=GEO_CRS)


# Create GeoJSONSeq file for vector tiles

df.geometry = from_pygeos(df.geometry)
df = gp.GeoDataFrame(df, crs=GEO_CRS)
df.to_file("/tmp/units.geojson", driver="GeoJSONSeq")
# TODO: use pyogrio
# df = gp.GeoDataFrame({"geometry": df.geometry, 'id': df.id},index=df.index, crs=GEO_CRS)
# write_dataframe(df, '/tmp/units.geojson', driver="GeoJSONSeq")


### Create mask by cutting SA bounds out of arbitrarily large polygon
src_dir = Path("source_data/boundaries")
out_dir = Path("data/boundaries")
sa_bnd = pio.read_dataframe(
    src_dir / "SALCCboundary.gdb", layer="SALCC_ACF", as_pygeos=True
)
sa_bnd = to_crs(sa_bnd.geometry, sa_bnd.crs, GEO_CRS)

# Clip boundary from outer box
outer = pg.box(-180, -85, 180, 85)
mask = pg.difference(outer, sa_bnd)

mask = from_pygeos(mask)

# TODO: port to poygrio
df = gp.GeoDataFrame({"geometry": mask}, crs=GEO_CRS)
df.to_file("/tmp/mask.geojson", driver="GeoJSONSeq")


### Extract counties within SA bounds
states = (
    pio.read_dataframe(src_dir / "source/tl_2019_us_state.shp", as_pygeos=True)[
        ["STATEFP", "NAME"]
    ]
    .rename(columns={"NAME": "state"})
    .set_index("STATEFP")
)

# coordinates are in geographic coordinates (NAD83 vs WGS84)
df = pio.read_dataframe(src_dir / "source/tl_2018_us_county.shp", as_pygeos=True)
crs = df.crs

in_bnd = sjoin(df, pd.DataFrame({"geometry": sa_bnd}), how="inner")

df = (
    in_bnd[["STATEFP", "GEOID", "NAME", "geometry"]]
    .rename(columns={"GEOID": "FIPS", "NAME": "county"})
    .join(states, on="STATEFP")
)
df = df[["FIPS", "state", "county", "geometry"]].reset_index(drop=True)

df["geometry"] = to_crs(df.geometry, crs, DATA_CRS)

to_geofeather(df, out_dir / "counties.feather", crs=DATA_CRS)

df["geometry"] = from_pygeos(df.geometry)

# DEBUG:
# df = gp.GeoDataFrame(df, crs=DATA_CRS)
# df.to_file("/tmp/counties.shp")


### Export protected areas to vector tiles
df = from_geofeather_as_gp(out_dir / "ownership.feather")
df.to_file("/tmp/ownership.geojson", driver="GeoJSONSeq")
