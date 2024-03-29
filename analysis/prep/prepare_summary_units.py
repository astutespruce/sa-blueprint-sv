from pathlib import Path
from pyogrio.geopandas import read_dataframe, write_dataframe
import pygeos as pg
import numpy as np

# suppress warnings abuot writing to feather
import warnings

warnings.filterwarnings("ignore", message=".*initial implementation of Parquet.*")


from analysis.constants import DATA_CRS, GEO_CRS, M2_ACRES


src_dir = Path("source_data")
data_dir = Path("data")
analysis_dir = data_dir / "inputs/summary_units"
bnd_dir = data_dir / "boundaries"  # GPKGs output for reference
tile_dir = data_dir / "for_tiles"

### Extract the boundary

sa_df = read_dataframe(src_dir / "boundaries/SouthAtlantic2021Extent.shp")[["geometry"]]
bnd = pg.make_valid(sa_df.geometry.values.data[0])

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
print("Selecting HUC12s in region...")
tree = pg.STRtree(huc12.geometry.values.data)
ix = tree.query(bnd, predicate="intersects")
huc12 = huc12.iloc[ix].copy().reset_index(drop=True)

huc12["acres"] = (pg.area(huc12.geometry.values.data) * M2_ACRES).round().astype("uint")

# for those at the edge, only keep the ones with > 50% in the extent
tree = pg.STRtree(huc12.geometry.values.data)
contains_ix = tree.query(bnd, predicate="contains")
edge_ix = np.setdiff1d(huc12.index, contains_ix)

overlap = pg.area(
    pg.intersection(huc12.iloc[edge_ix].geometry.values.data, bnd)
) / pg.area(huc12.iloc[edge_ix].geometry.values.data)
keep_ix = np.append(contains_ix, edge_ix[overlap >= 0.5])
keep_ix.sort()

huc12 = huc12.iloc[keep_ix].copy()

huc12_wgs84 = huc12.to_crs(GEO_CRS)
huc12 = huc12.join(huc12_wgs84.bounds)

huc12.to_feather(analysis_dir / "huc12.feather")
write_dataframe(huc12, bnd_dir / "huc12.gpkg", driver="GPKG")


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

marine_wgs84 = marine.to_crs(GEO_CRS)
marine = marine.join(marine_wgs84.bounds)

marine.to_feather(analysis_dir / "marine_blocks.feather")
write_dataframe(marine, bnd_dir / "marine_blocks.gpkg", driver="GPKG")


### Merge HUC12 and marine into single units file and export for creating tiles
df = huc12_wgs84.append(marine_wgs84, ignore_index=True, sort=False)
write_dataframe(df, tile_dir / "units.geojson", driver="GeoJSONSeq")
