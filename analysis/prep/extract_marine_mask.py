from pathlib import Path

import numpy as np
import geopandas as gp
import pygeos as pg
from pyogrio.geopandas import read_dataframe, write_dataframe
import rasterio
from rasterio.features import shapes


ecosystems_path = Path(
    "source_data/blueprint/EcosystemMask_20160229_Blueprint_2_1_AnalysisArea.tif"
)
out_dir = Path("data")

with rasterio.open(ecosystems_path) as src:
    data = src.read()
    marine = (data == 22).astype("uint8")
    transform = src.transform
    crs = src.crs


features = list(shapes(marine, mask=marine, transform=transform))

polygons = np.empty(shape=(len(features)), dtype="object")
for i, (feature, value) in enumerate(features):
    exterior = feature["coordinates"][0]
    interiors = feature["coordinates"][1:]
    if interiors:
        geom = pg.polygons(exterior, [pg.linearrings(r) for r in interiors])
    else:
        geom = pg.polygons(exterior)

    polygons[i] = geom

# TODO: union all

df = gp.GeoDataFrame({"geometry": polygons}, crs=crs)

write_dataframe(df, "/tmp/marine_mask.gpkg", driver="GPKG")


df = read_dataframe("source_data/summary_units/huc12_prj.shp")
inland_mask = pg.union_all(df.geometry.values.data)

write_dataframe(
    gp.GeoDataFrame({"geometry": inland_mask}, index=[0], crs=df.crs),
    "/tmp/inland_mask.gpkg",
    driver="GPKG",
)

