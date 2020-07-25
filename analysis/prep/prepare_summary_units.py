import os
from pathlib import Path
import geopandas as gp
import pandas as pd
from pyogrio.geopandas import read_dataframe, write_dataframe
import pygeos as pg

from analysis.constants import DATA_CRS, GEO_CRS, M2_ACRES


src_dir = Path("source_data")
data_dir = Path("data")
analysis_dir = data_dir / "summary_units"
results_dir = data_dir / "results"

### Extract the boundary

# TODO: use new SA boundary
sa_df = read_dataframe(src_dir / "boundaries/SALCCboundary.gdb", layer="SALCC_ACF")[
    ["geometry"]
]


### Extract HUC12 within boundary

print("Reading source HUC12s...")
merged = None
for huc2 in [2, 3, 5, 6]:
    df = read_dataframe(
        src_dir / f"summary_units/WBD_0{huc2}_HU2_GDB/WBD_0{huc2}_HU2_GDB.gdb",
        layer="WBDHU12",
    )[["huc12", "name", "geometry"]].rename(columns={"huc12": "id"})

    if merged is None:
        merged = df

    else:
        merged = merged.append(df, ignore_index=True)

print("Projecting to match SA data...")
huc12 = merged.to_crs(DATA_CRS)

# make sure data are valid
huc12["geometry"] = pg.make_valid(huc12.geometry.values.data)


# select out those within the SA boundary
tree = pg.STRtree(huc12.geometry.values.data)
ix = tree.query(sa_df.geometry.values.data[0], predicate="intersects")
huc12 = huc12.iloc[ix].copy()

huc12["acres"] = (pg.area(huc12.geometry.values.data) * M2_ACRES).round().astype("uint")

# Save in EPSG:5070 for analysis
write_dataframe(huc12, analysis_dir / "huc12.gpkg", driver="GPKG")
huc12.to_feather(analysis_dir / "huc12.feather")

# project to WGS84 for report maps and vector tiles
huc12_wgs84 = huc12.to_crs(GEO_CRS)
out_dir = results_dir / "huc12"
if not out_dir.exists():
    os.makedirs(out_dir)

huc12_wgs84.to_feather(out_dir / "huc12_wgs84.feather")


### Marine units (already in EPSG:5070)
print("Reading marine blocks...")
marine = read_dataframe(src_dir / "summary_units/marine_blocks_prj.shp")[
    ["PROT_NUMBE", "BLOCK_NUMB", "geometry"]
]
marine["id"] = marine.PROT_NUMBE.str.strip() + "-" + marine.BLOCK_NUMB.str.strip()
marine["name"] = (
    marine.PROT_NUMBE.str.strip() + ": Block " + marine.BLOCK_NUMB.str.strip()
)
marine = marine[["id", "name", "geometry"]].to_crs(DATA_CRS)

marine["geometry"] = pg.make_valid(marine.geometry.values.data)


marine["acres"] = (
    (pg.area(marine.geometry.values.data) * M2_ACRES).round().astype("uint")
)

# Save in EPSG:5070 for analysis
write_dataframe(marine, analysis_dir / "marine.gpkg", driver="GPKG")
marine.to_feather(analysis_dir / "marine.feather")

# project to WGS84 for report maps and vector tiles
marine_wgs84 = marine.to_crs(GEO_CRS)
out_dir = results_dir / "marine_blocks"
if not out_dir.exists():
    os.makedirs(out_dir)

marine_wgs84.to_feather(out_dir / "marine_blocks_wgs84.feather")


### Merge HUC12 and marine into single units file and export for creating tiles
df = huc12_wgs84.append(marine_wgs84, ignore_index=True, sort=False)
write_dataframe(df, analysis_dir / "units_wgs84.gpkg", driver="GPKG")
