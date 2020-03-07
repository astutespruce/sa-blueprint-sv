from pathlib import Path
import csv
from time import time

import pandas as pd
import geopandas as gp

# from geofeather.pygeos import from_geofeather
from geofeather import from_geofeather
import numpy as np
import pygeos as pg
import rasterio
from rasterio.mask import raster_geometry_mask

from util.io import write_raster
from constants import BLUEPRINT, INDICATORS
from stats import extract_count_in_geometry, extract_blueprint_indicator_counts


data_dir = Path("data")
out_dir = data_dir / "derived"
huc12_filename = data_dir / "summary_units/HUC12.feather"

start = time()

# TODO: pygeos version and map to __geo_interface__
geometries = from_geofeather(huc12_filename, columns=["geometry"]).geometry

results = []
for i, geometry in geometries.iteritems():
    results.append(extract_blueprint_indicator_counts([geometry]))

df = pd.DataFrame(results)


mask = df[["mask"]]
mask.columns = [f"{c}_count" for c in mask.columns]
mask.to_feather(out_dir / "mask.feather")
mask.to_csv(out_dir / "mask.csv", index_label="id")

for col in df.columns:
    s = df[col].apply(pd.Series).astype("uint32")
    s.columns = [f"{c}_count" for c in s.columns]
    s.to_feather(out_dir / f"{col}.feather")
    s.to_csv(out_dir / f"{col}.csv", index_label="id")


print("Processed {} zones in {:.2f}s".format(len(geometries), time() - start))

