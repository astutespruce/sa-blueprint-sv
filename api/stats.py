"""
standard projection is: ESRI:102039 / EPSG:5070 (CONUS albers)

to convert to projection (can also add simplify option and drop attributes, but need to know which one to keep)
ogr2ogr -overwrite -t_srs "EPSG:5070" ACF_prj.shp ACF_area.shp

"""

from pathlib import Path
from time import time

import rasterio
from rasterio.mask import raster_geometry_mask
import geopandas as gp
import numpy as np
import pandas as pd

from constants import BLUEPRINT, ECOSYSTEMS, INDICATORS_INDEX


def extract_count_in_geometry(filename, geometry_mask, window, bins):
    """Apply the geometry mask to values read from filename, and generate a list
    of pixel counts for each bin in bins.

    Parameters
    ----------
    filename : str
        input GeoTIFF filename
    geometry_mask : 2D boolean ndarray
        True for all pixels outside geometry, False inside.
    window : rasterio.windows.Window
        Window that defines the footprint of the geometry_mask within the raster.
    bins : list-like
        List-like of values ranging from 0 to max value (not sparse!).
        Counts will be generated that correspond to this list of bins.

    Returns
    -------
    ndarray
        Total number of pixels for each bin
    """

    with rasterio.open(filename) as src:
        data = src.read(1, window=window)
        nodata = src.nodatavals[0]

    mask = (data == nodata) | geometry_mask

    # slice out flattened array of values that are not masked
    values = data[~mask]

    # count number of pixels in each bin
    counts = np.bincount(values, minlength=len(bins))
    return counts


src_dir = Path("data")
blueprint_filename = src_dir / "Blueprint_2_2.tif"
slr_filename = src_dir / "threats" / f"slr_binned.tif"

start = time()

# TODO: project file before passing in here?
# Or do it all in memory from zipfile received by API?
df = gp.read_file(src_dir / "aoi" / "Razor_prj.shp")[["geometry"]]
geometries = df.geometry.values

### create the mask
with rasterio.open(blueprint_filename) as src:
    geometry_mask, transform, window = raster_geometry_mask(
        src, geometries, crop=True  # , all_touched=True
    )
    # square meters to acres
    cellsize = src.res[0] * src.res[1] * 0.000247105
    geometry_area = (~geometry_mask).sum() * cellsize

    meta = src.meta.copy()
    meta["width"] = geometry_mask.shape[1]
    meta["height"] = geometry_mask.shape[0]
    meta["transform"] = transform

    with rasterio.open("/tmp/mask.tif", "w", **meta) as out:
        out.write(geometry_mask.astype("int8"), 1)


# TODO: if not (window.width and window.height) then bail early; not in SA region


### Calculate Blueprint stats
bins = np.arange(0, len(BLUEPRINT))
counts = extract_count_in_geometry(blueprint_filename, geometry_mask, window, bins)
area = (counts * cellsize).astype("float32")
percent = 100 * (area / geometry_area).astype("float32")

blueprint_results = pd.DataFrame({"value": bins, "acres": area, "percent": percent})

print("Blueprint", blueprint_results)

print("\n-------------\nIndicators:")

### Calculate stats by indicator; 200m grid
indicator_results = {}
for entry in ECOSYSTEMS:
    ecosystem = entry["id"]
    for indicator in entry["indicators"]:
        id = f"{ecosystem}_{indicator}"
        indicator = INDICATORS_INDEX[id]
        filename = src_dir / "indicators" / indicator["filename"]
        values = indicator["values"].keys()

        bins = np.arange(0, max(values) + 1)
        counts = extract_count_in_geometry(filename, geometry_mask, window, bins)
        area = (counts * cellsize).astype("float32")
        percent = 100 * (area / geometry_area).astype("float32")

        results = pd.DataFrame({"value": bins, "acres": area, "percent": percent})
        # drop any values from [0...max] that were not present in original values (usually 0's)
        results = results[results.value.isin(values)].copy()
        indicator_results[id] = results

        print(id, results)

### Calculate urbanization stats; 60m grid
with rasterio.open(src_dir / "threats" / "serap_urb2020_IsNull0.tif") as src:
    geometry_mask, transform, window = raster_geometry_mask(src, geometries, crop=True)

    # square meters to acres
    cellsize = src.res[0] * src.res[1] * 0.000247105
    geometry_area = (~geometry_mask).sum() * cellsize


# values are probability of urbanization per timestep * 1000 (uint16)
years = [2020, 2030, 2040, 2050, 2060, 2070, 2080, 2090, 2100]
probabilities = (
    np.array(
        [0, 1, 25, 50, 100, 200, 300, 400, 500, 600, 700, 800, 900, 950, 975, 1000]
    )
    / 1000
)
bins = np.arange(0, len(probabilities))

print("Processing urbanization")
urban_results = None
if window.width and window.height:
    urban_percents = []
    for year in years:
        print(year)
        filename = src_dir / "threats" / f"urb_indexed_{year}.tif"
        counts = extract_count_in_geometry(filename, geometry_mask, window, bins)
        # percent urbanization is sum of area of each pixel * probability
        percent = 100 * (counts * probabilities * cellsize).sum() / geometry_area
        urban_percents.append(percent)

    urban_results = pd.DataFrame({"year": years, "percent": urban_percents})

    print("urbanization", urban_results)


### SLR; 30m grid
slr_results = None
with rasterio.open(slr_filename) as src:
    geometry_mask, transform, window = raster_geometry_mask(src, geometries, crop=True)
    # square meters to acres
    cellsize = src.res[0] * src.res[1] * 0.000247105
    geometry_area = (~geometry_mask).sum() * cellsize

if window.width and window.height:
    bins = [0, 1, 2, 3, 4, 5, 6]  # SLR in foot increments up to 6
    counts = extract_count_in_geometry(slr_filename, geometry_mask, window, bins)

    area = (counts * cellsize).astype("float32")
    percent = 100 * (area / geometry_area).astype("float32")

    slr_results = pd.DataFrame({"slr_ft": bins, "acres": area, "percent": percent})
    print("slr", slr_results)


print("All done in {:.2f}s".format(time() - start))

