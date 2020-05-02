""" Calculate the bounds of each SLR GeoTIFF and save for spatial index later """
from pathlib import Path

import rasterio
import geopandas as gp
from shapely.geometry import box
from geofeather import to_geofeather


data_dir = Path("data")
src_dir = data_dir / "threats/slr/source"

boxes = []
for filename in (src_dir / "NOAA_Inundation_allft_tif").glob("*.tif"):
    with rasterio.open(filename) as src:
        boxes.append(box(*src.bounds))

df = gp.GeoDataFrame({"geometry": boxes}, crs=src.crs)
to_geofeather(df, src_dir / "slr_bounds.feather")

