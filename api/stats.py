"""
standard projection is: ESRI:102039 / EPSG:5070 (CONUS albers)

to convert to projection (can also add simplify option and drop attributes, but need to know which one to keep)
ogr2ogr -overwrite -t_srs "EPSG:5070" ACF_prj.shp ACF_area.shp

"""

from pathlib import Path

import rasterio
from rasterio.mask import raster_geometry_mask
import geopandas as gp
import numpy as np

from constants import BLUEPRINT, ECOSYSTEMS, INDICATORS_INDEX


src_dir = Path("data")
blueprint_filename = src_dir / "Blueprint_2_2.tif"


# TODO: project file before passing in here?
# Or do it all in memory from zipfile received by API?
df = gp.read_file(src_dir / "tmp" / "ACF_prj.shp")[["geometry"]]

### create the mask
with rasterio.open(blueprint_filename) as src:
    mask, transform, window = raster_geometry_mask(src, df.geometry.values, crop=True)


### Calculate Blueprint stats
bins = np.arange(0, len(BLUEPRINT))
counts = apply_mask_to_raster(blueprint_filename, mask, window, bins)
print("Blueprint:")
print(bins, counts)

print("\n-------------\nIndicators:")

### Calculate stats by indicator
for entry in ECOSYSTEMS:
    ecosystem = entry["id"]
    for indicator in entry["indicators"]:
        id = f"{ecosystem}_{indicator}"
        indicator = INDICATORS_INDEX[id]
        filename = src_dir / "indicators" / indicator["filename"]
        bins = np.arange(0, max(indicator["values"].keys()) + 1)
        counts = apply_mask_to_raster(filename, mask, window, bins)

        print(id, bins, counts)


def apply_mask_to_raster(filename, geometry_mask, window, bins):
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
        Pixel count for each bin
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
