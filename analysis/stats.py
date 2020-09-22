import math
from pathlib import Path

import numpy as np
import pandas as pd
import rasterio
from rasterio.features import bounds
from rasterio.mask import raster_geometry_mask, geometry_mask
from rasterio.windows import Window

from analysis.constants import (
    BLUEPRINT,
    INDICATORS,
    CORRIDORS,
    URBAN_YEARS,
    ACRES_PRECISION,
    M2_ACRES,
)

src_dir = Path("data/inputs")
indicators_dir = src_dir / "indicators"
continuous_indicator_dir = Path("data/continuous_indicators")
indicators_mask_dir = indicators_dir / "masks"
blueprint_filename = src_dir / "blueprint2020.tif"
corridors_filename = src_dir / "corridors.tif"
urban_dir = src_dir / "threats/urban"
slr_dir = src_dir / "threats/slr"


def boundless_raster_geometry_mask(dataset, shapes, bounds, all_touched=True):
    """Alternative to rasterio.mask::raster_geometry_mask that allows boundless
    reads from raster data sources.

    Parameters
    ----------
    dataset : open rasterio dataset
    shapes : list-like of geometry objects that provide __geo_interface__
    bounds : list-like of [xmin, ymin, xmax, ymax]
    all_touched : bool, optional (default: True)
    """

    # Calculate outer window that contains bounds
    window = dataset.window(
        *bounds
    )  # .round_offsets(op="floor").round_lengths(op="ceil")
    window_floored = window.round_offsets(op="floor", pixel_precision=3)
    w = math.ceil(window.width + window.col_off - window_floored.col_off)
    h = math.ceil(window.height + window.row_off - window_floored.row_off)
    window = Window(window_floored.col_off, window_floored.row_off, w, h)

    transform = dataset.window_transform(window)
    out_shape = (int(window.height), int(window.width))
    mask = geometry_mask(
        shapes, transform=transform, out_shape=out_shape, all_touched=all_touched
    )

    return mask, transform, window


def extract_count_in_geometry(filename, geometry_mask, window, bins, boundless=False):
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
    boundless : bool (default: False)
        If True, will use boundless reads of the data.  This must be used
        if the window extends beyond the extent of the dataset.

    Returns
    -------
    ndarray
        Total number of pixels for each bin
    """

    with rasterio.open(filename) as src:
        data = src.read(1, window=window, boundless=boundless)
        nodata = src.nodatavals[0]

    mask = (data == nodata) | geometry_mask

    # slice out flattened array of values that are not masked
    values = data[~mask]

    # count number of pixels in each bin
    return np.bincount(values, minlength=len(bins)).astype("uint32")


def extract_zonal_mean(filename, geometry_mask, window, boundless=False):
    """Apply the geometry mask to values read from filename and calculate
    the mean within that area.

    Parameters
    ----------
    filename : str
        input GeoTIFF filename
    geometry_mask : 2D boolean ndarray
        True for all pixels outside geometry, False inside.
    window : rasterio.windows.Window
        Window that defines the footprint of the geometry_mask within the raster.
    boundless : bool (default: False)
        If True, will use boundless reads of the data.  This must be used
        if the window extends beyond the extent of the dataset.
    Returns
    -------
    float
        will be nan where there is no data within mask
    """

    with rasterio.open(filename) as src:
        data = src.read(1, window=window, boundless=boundless)
        nodata = src.nodatavals[0]

    mask = (data == nodata) | geometry_mask

    # since mask is True everywhere it is masked OUT, if the min is
    # True, then there is no data
    if mask.min():
        return np.nan

    # slice out flattened array of values that are not masked
    # and calculate the mean
    return data[~mask].mean()


def detect_indicators(geometries, indicators):
    """Check area of interest against coarse resolution indicator mask for
    each indicator to see if indicator is present in this area.

    Parameters
    ----------
    geometries : list-like of geometry objects that provide __geo_interface__
    indicators : list-like of indicator IDs

    Returns
    -------
    list of indicator IDs present in area
    """

    if not indicators:
        return []

    with rasterio.open(indicators_mask_dir / indicators[0]["filename"]) as src:
        geometry_mask, transform, window = raster_geometry_mask(
            src, geometries, crop=True, all_touched=True
        )

    indicators_with_data = []
    for indicator in indicators:
        with rasterio.open(indicators_mask_dir / indicator["filename"]) as src:
            data = src.read(1, window=window)
            nodata = src.nodatavals[0]

            mask = (data == nodata) | geometry_mask

        # if there are unmasked areas, keep this indicator
        if mask.min() == False:
            indicators_with_data.append(indicator)

    return indicators_with_data


def extract_blueprint_indicator_area(
    geometries, bounds, inland=True, zonal_means=False
):
    """Calculate the area of overlap between geometries and Blueprint, indicators,
    and corridors.

    NOTE: Blueprint, indicators, and corridors are on the same 200m grid.

    Parameters
    ----------
    geometries : list-like of geometry objects that provide __geo_interface__
    bounds : list-like of [xmin, ymin, xmax, ymax]
    inland : bool (default False)
        if False will use only marine indicators
    zonal_means : bool (default False)
        if True, results will include zonal means of continuous indicators

    Returns
    -------
    dict or None (if does not overlap Blueprint data)
        {"counts": {"<indicator_id>": [...], ...}, "means": {"<indicator_id>": <mean>, }}
        Keys of counts are mask, blueprint, <indicator_id>, ...
        values are total areas for each value in each theme.
        Keys of means are <indicator_id> for continuous indicators only, values are
        means.
    """

    results = {"counts": {}, "means": {}}

    # create mask and window
    with rasterio.open(blueprint_filename) as src:
        try:
            geometry_mask, transform, window = boundless_raster_geometry_mask(
                src, geometries, bounds, all_touched=True
            )

        except ValueError:
            return None

        # square meters to acres
        cellsize = src.res[0] * src.res[1] * M2_ACRES

    results["counts"]["shape_mask"] = (
        ((~geometry_mask).sum() * cellsize)
        .round(ACRES_PRECISION)
        .astype("float32")
        .round(ACRES_PRECISION)
        .astype("float32")
    )

    # Does not overlap Blueprint extent, return
    if results["counts"]["shape_mask"] == 0:
        return None

    blueprint_counts = extract_count_in_geometry(
        blueprint_filename,
        geometry_mask,
        window,
        np.arange(len(BLUEPRINT)),
        boundless=True,
    )
    results["counts"]["blueprint"] = (
        (blueprint_counts * cellsize).round(ACRES_PRECISION).astype("float32")
    )
    blueprint_total = blueprint_counts.sum()

    corridor_counts = extract_count_in_geometry(
        corridors_filename,
        geometry_mask,
        window,
        np.arange(len(CORRIDORS)),
        boundless=True,
    )
    results["counts"]["corridors"] = (
        (corridor_counts * cellsize).round(ACRES_PRECISION).astype("float32")
    )

    if inland:
        # since some HUCs overlap marine areas, we include all indicators
        # that are present in area
        indicators = detect_indicators(geometries, INDICATORS)

    else:
        # marine areas only have marine indicators
        # Note: no need to run detect_indicators(), all are present everywhere
        # in marine area.
        indicators = [i for i in INDICATORS if i["id"].startswith("marine_")]
        indicators = detect_indicators(geometries, indicators)

    for indicator in indicators:
        id = indicator["id"]
        filename = indicators_dir / indicator["filename"]

        values = [e["value"] for e in indicator["values"]]
        bins = np.arange(0, max(values) + 1)
        counts = extract_count_in_geometry(
            filename, geometry_mask, window, bins, boundless=True
        )

        # Some indicators exclude 0 values, their counts need to be zeroed out here
        min_value = min(values)
        if min_value > 0:
            counts[range(0, min_value)] = 0

        results["counts"][id] = (
            (counts * cellsize).round(ACRES_PRECISION).astype("float32")
        )

        if zonal_means and indicator.get("continuous"):
            continuous_filename = continuous_indicator_dir / indicator[
                "filename"
            ].replace("_Binned", "")
            mean = extract_zonal_mean(
                continuous_filename, geometry_mask, window, boundless=True
            )
            if mean is not None:
                results["means"][id] = mean

    return results


def extract_urbanization_area(geometries, bounds):
    """Calculate the area of overlap between geometries and urbanization
    for each decade from 2020 to 2100.

    This is only applicable to inland (non-marine) areas.

    NOTE: urbanization is on a 60m grid

    Parameters
    ----------
    geometries : list-like of geometry objects that provide __geo_interface__
    bounds : list-like of [xmin, ymin, xmax, ymax]

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
            geometry_mask, transform, window = boundless_raster_geometry_mask(
                src, geometries, bounds, all_touched=True
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
        counts = extract_count_in_geometry(
            filename, geometry_mask, window, bins, boundless=True
        )

        if year == 2020:
            # extract area already urban (in index 1)
            results["urban"] = (
                (counts[1] * cellsize).round(ACRES_PRECISION).astype("float32")
            )

        # total urbanization is sum of pixel counts * probability
        results[year] = (
            ((counts * probabilities).sum() * cellsize)
            .round(ACRES_PRECISION)
            .astype("float32")
        )

    return results


def extract_slr_area(geometries, bounds):
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
    bounds : list-like of [xmin, ymin, xmax, ymax]

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
            geometry_mask, transform, window = boundless_raster_geometry_mask(
                src, geometries, bounds, all_touched=True
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
    counts = extract_count_in_geometry(
        vrt, geometry_mask, window, bins=bins, boundless=True
    )

    # accumulate values
    for bin in bins[1:]:
        counts[bin] = counts[bin] + counts[bin - 1]

    acres = (counts * cellsize).round(ACRES_PRECISION).astype("float32")
    results.update({i: a for i, a in enumerate(acres)})

    return results
