from pathlib import Path
import geopandas as gp

from geofeather import to_geofeather
from constants import DATA_CRS

src_dir = Path("data/summary_units")

# It's already in that projection but has wrong EPSG code assigned by ArcGIS
df = gp.read_file(src_dir / "HUC12_prj.shp").to_crs(DATA_CRS)
to_geofeather(df, src_dir / "huc12.feather")

df = gp.read_file(src_dir / "marine_blocks_prj.shp").to_crs(DATA_CRS)
to_geofeather(df, src_dir / "marine_blocks.feather")
