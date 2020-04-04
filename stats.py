from pathlib import Path

import numpy as np
import pandas as pd
import rasterio
from rasterio.mask import raster_geometry_mask

from constants import (
    BLUEPRINT,
    ECOSYSTEMS,
    INDICATORS,
    URBAN_YEARS,
    ACRES_PRECISION,
    M2_ACRES,
)

src_dir = Path("data")
blueprint_filename = src_dir / "Blueprint_2_2.tif"
ecosystems_filename = src_dir / "ecosystems_indexed.tif"
urban_dir = src_dir / "threats/urban"
slr_dir = src_dir / "threats/slr"


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
    return np.bincount(values, minlength=len(bins)).astype("uint32")


def extract_blueprint_indicator_area(geometries, inland=True):
    """Calculate the area of overlap between geometries and Blueprint and indicators.

    NOTE: Blueprint and indicators are on a 30m grid.

    Parameters
    ----------
    geometries : list-like of geometry objects that provide __geo_interface__
    inland : bool (default False)
        if False will use only marine indicators

    Returns
    -------
    dict or None (if does not overlap Blueprint data)
        keys are mask, blueprint, <indicator_id>, ...
        values are total areas for each value in each theme
    """
    results = {}
    # create mask and window
    with rasterio.open(blueprint_filename) as src:
        try:
            geometry_mask, transform, window = raster_geometry_mask(
                src, geometries, crop=True, all_touched=True
            )

        except ValueError:
            return None

        # square meters to acres
        cellsize = src.res[0] * src.res[1] * M2_ACRES

    results["shape_mask"] = (
        ((~geometry_mask).sum() * cellsize).round(ACRES_PRECISION).astype("float32")
    )

    # Does not overlap Blueprint extent, return
    if results["shape_mask"] == 0:
        return None

    blueprint_counts = extract_count_in_geometry(
        blueprint_filename, geometry_mask, window, np.arange(len(BLUEPRINT))
    )
    results["blueprint"] = (
        (blueprint_counts * cellsize).round(ACRES_PRECISION).astype("float32")
    )

    if inland:
        # since some HUCs overlap marine areas, we should include all indicators
        indicators = INDICATORS

        ecosystem_counts = extract_count_in_geometry(
            ecosystems_filename, geometry_mask, window, np.arange(9)
        )
        results["ecosystems"] = (
            (ecosystem_counts * cellsize).round(ACRES_PRECISION).astype("float32")
        )
    else:
        # marine areas only have marine indicators
        indicators = [i for i in INDICATORS if i["id"].startswith("marine_")]

    for indicator in indicators:
        id = indicator["id"]
        filename = src_dir / "indicators" / indicator["filename"]
        values = indicator["values"].keys()

        bins = np.arange(0, max(values) + 1)
        counts = extract_count_in_geometry(filename, geometry_mask, window, bins)
        results[id] = (counts * cellsize).round(ACRES_PRECISION).astype("float32")

    return results


def extract_urbanization_area(geometries):
    """Calculate the area of overlap between geometries and urbanization
    for each decade from 2020 to 2100.

    This is only applicable to inland (non-marine) areas.

    NOTE: urbanization is on a 60m grid

    Parameters
    ----------
    geometries : list-like of geometry objects that provide __geo_interface__

    Returns
    -------
    dict
        keys are mask, <decade>, ...
        values are the total acres of urbanization for each decade
    """
    results = {}

    # create mask and window
    with rasterio.open(urban_dir / "urb_indexed_2020.tif") as src:
        try:
            geometry_mask, transform, window = raster_geometry_mask(
                src, geometries, crop=True, all_touched=True
            )

        except ValueError:
            return None

        # square meters to acres
        cellsize = src.res[0] * src.res[1] * M2_ACRES

    results["shape_mask"] = (
        ((~geometry_mask).sum() * cellsize).round(ACRES_PRECISION).astype("float32")
    )

    if results["shape_mask"] == 0:
        return None

    # values are probability of urbanization per timestep * 1000 (uint16)
    # NOTE: index 0 = not predicted to urbanize
    # index 1 = already urban, so given a probability of 1
    # actual probabilities start at 0.025
    probabilities = (
        np.array(
            [
                0,
                1000,
                25,
                50,
                100,
                200,
                300,
                400,
                500,
                600,
                700,
                800,
                900,
                950,
                975,
                1000,
            ]
        )
        / 1000
    )
    bins = np.arange(0, len(probabilities))

    for year in URBAN_YEARS:
        filename = urban_dir / f"urb_indexed_{year}.tif"
        counts = extract_count_in_geometry(filename, geometry_mask, window, bins)
        # total urbanization is sum of pixel counts * probability
        results[year] = (
            ((counts * probabilities).sum() * cellsize)
            .round(ACRES_PRECISION)
            .astype("float32")
        )

    return results


def extract_slr_area(geometries):
    """Calculate the area of overlap between geometries and each level of SLR
    between 0 (currently inundated) and 6 meters.

    Values are cumulative; the total area inundated is added to each higher
    level of SLR

    This is only applicable to inland (non-marine) areas that are near the coast.

    NOTE: SLR is in a VRT with a cell size derived from the underlying rasters.

    Parameters
    ----------
    geometries : list-like of geometry objects that provide __geo_interface__
        Should be limited to features that intersect with bounds of SLR datasets

    Returns
    -------
    dict
        keys are mask, <decade>, ...
        values are the area of incremental (not total!) sea level rise by foot
    """
    vrt = slr_dir / "slr.vrt"

    results = {}

    # create mask and window
    with rasterio.open(vrt) as src:
        try:
            geometry_mask, transform, window = raster_geometry_mask(
                src, geometries, crop=True, all_touched=True
            )

        except ValueError:
            return None

        # square meters to acres
        cellsize = src.res[0] * src.res[1] * M2_ACRES

        data = src.read(1, window=window)
        nodata = src.nodatavals[0]
        mask = (data == nodata) | geometry_mask
        data = np.where(mask, nodata, data)

    results["shape_mask"] = (
        ((~geometry_mask).sum() * cellsize).round(ACRES_PRECISION).astype("float32")
    )

    if results["shape_mask"] == 0:
        return None

    bins = np.arange(7)
    counts = extract_count_in_geometry(vrt, geometry_mask, window, bins=bins)

    # accumulate values
    for bin in bins[1:]:
        counts[bin] = counts[bin] + counts[bin - 1]

    acres = (counts * cellsize).round(ACRES_PRECISION).astype("float32")
    results.update({i: a for i, a in enumerate(acres)})

    return results
