from pathlib import Path
import geopandas as gp
import pandas as pd
import pyogrio as pio
from geofeather.pygeos import from_geofeather, to_geofeather
import pygeos as pg

from analysis.constants import DATA_CRS, GEO_CRS, M2_ACRES
from analysis.pygeos_util import to_crs, sjoin, explode

data_dir = Path("data")
unit_dir = data_dir / "summary_units"
out_dir = data_dir / "derived"
boundary_dir = data_dir / "boundaries"


### Inland (HUC12) summary units

# It's already in that projection but has wrong EPSG code assigned by ArcGIS
print("Reading HUC12...")
huc12 = (
    pio.read_dataframe(unit_dir / "HUC12_prj.shp", as_pygeos=True)[
        ["geometry", "HUC12", "HU_12_NAME"]
    ]
    .set_index("HUC12")
    .rename(columns={"HU_12_NAME": "name"})
)

# save for analysis
to_geofeather(
    huc12[["geometry"]].reset_index(), unit_dir / "huc12_prj.feather", crs=DATA_CRS
)

# calculate area in native projection
huc12["acres"] = pg.area(huc12.geometry) * M2_ACRES

# reproject to WGS84
huc12.geometry = to_crs(huc12.geometry, DATA_CRS, GEO_CRS)
to_geofeather(huc12.reset_index(), out_dir / "huc12" / "huc12.feather", crs=GEO_CRS)


### Marine summary units
print("Reading marine blocks...")
marine = pio.read_dataframe(unit_dir / "marine_blocks_prj.shp", as_pygeos=True)[
    ["PROT_NUMBE", "BLOCK_NUMB", "geometry"]
]
marine["id"] = marine.PROT_NUMBE.str.strip() + "-" + marine.BLOCK_NUMB.str.strip()
marine = marine.set_index("id")
marine["name"] = (
    marine.PROT_NUMBE.str.strip() + ": Block " + marine.BLOCK_NUMB.str.strip()
)
marine = marine[["name", "geometry"]]

# save for analysis
to_geofeather(
    marine[["geometry"]].reset_index(),
    unit_dir / "marine_blocks_prj.feather",
    crs=DATA_CRS,
)

# calculate area
marine["acres"] = pg.area(marine.geometry) * M2_ACRES

# reproject to WGS84 for mapping
marine.geometry = to_crs(marine.geometry, DATA_CRS, GEO_CRS)
to_geofeather(marine.reset_index(), out_dir / "marine_blocks" / "marine_blocks.feather")


### Extract the boundary
sa_df = pio.read_dataframe(boundary_dir / "source/SALCCboundary.gdb", as_pygeos=True)[
    ["geometry"]
]

### Process TNC secured lands
print("Processing TNC secured lands...")

# This is in same projection as standard
df = pio.read_dataframe(
    boundary_dir / "source/TNC_SA2018_InterimPublic.gdb", as_pygeos=True
)[["FEE_ORGTYP", "GAP_STATUS", "geometry"]]

# Select out areas within the SA boundary
df = sjoin(df, sa_df, how="inner")


df.geometry = pg.make_valid(df.geometry)

# TODO: explode the multipolygons for better indexing (~1.1k polys)
df = explode(df)

to_geofeather(
    df[["FEE_ORGTYP", "GAP_STATUS", "geometry"]].reset_index(drop=True),
    boundary_dir / "ownership.feather",
    crs=DATA_CRS,
)
