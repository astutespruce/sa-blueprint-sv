from pathlib import Path
import pygeos as pg
import geopandas as gp
from geofeather import from_geofeather, to_geofeather

from util.pygeos_util import to_pygeos, from_pygeos
from constants import GEO_CRS

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
