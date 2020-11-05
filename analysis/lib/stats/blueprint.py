import math
from pathlib import Path

from progress.bar import Bar
import numpy as np
import pandas as pd
import pygeos as pg
import rasterio
from rasterio.mask import raster_geometry_mask

from analysis.constants import (
    BLUEPRINT,
    INDICATORS,
    CORRIDORS,
    ACRES_PRECISION,
    M2_ACRES,
)
from analysis.lib.raster import (
    boundless_raster_geometry_mask,
    extract_count_in_geometry,
    extract_zonal_mean,
)
from analysis.lib.pygeos_util import to_dict

src_dir = Path("data/inputs")
indicators_dir = src_dir / "indicators"
continuous_indicator_dir = src_dir / "continuous_indicators"
indicators_mask_dir = indicators_dir / "masks"
blueprint_filename = src_dir / "blueprint2020.tif"
corridors_filename = src_dir / "corridors.tif"


huc12_results_filename = "data/results/huc12/blueprint.feather"
marine_results_filename = "data/results/marine_blocks/blueprint.feather"


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


def extract_by_geometry(geometries, bounds, marine=False):
    """Calculate the area of overlap between geometries and Blueprint,
    corridors, and indicators.

    NOTE: Blueprint, indicators, and corridors are on the same 30m grid.

    Parameters
    ----------
    geometries : list-like of geometry objects that provide __geo_interface__
    bounds : list-like of [xmin, ymin, xmax, ymax]
    marine : bool (default False)
        if True will use only marine indicators

    Returns
    -------
    dict or None (if does not overlap)
    """

    results = {"counts": {}, "means": {}}

    # create mask and window
    with rasterio.open(blueprint_filename) as src:
        try:
            shape_mask, transform, window = boundless_raster_geometry_mask(
                src, geometries, bounds, all_touched=True
            )

        except ValueError:
            return None

        # square meters to acres
        cellsize = src.res[0] * src.res[1] * M2_ACRES

    results["counts"]["shape_mask"] = (
        ((~shape_mask).sum() * cellsize)
        .round(ACRES_PRECISION)
        .astype("float32")
        .round(ACRES_PRECISION)
        .astype("float32")
    )

    # Nothing in shape mask, return None
    # NOTE: this does not detect that area is completely outside SA area
    if results["counts"]["shape_mask"] == 0:
        return None

    blueprint_counts = extract_count_in_geometry(
        blueprint_filename,
        shape_mask,
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
        shape_mask,
        window,
        np.arange(len(CORRIDORS)),
        boundless=True,
    )
    results["counts"]["corridors"] = (
        (corridor_counts * cellsize).round(ACRES_PRECISION).astype("float32")
    )

    if marine:
        # marine areas only have marine indicators
        # Note: no need to run detect_indicators(), all are present everywhere
        # in marine area.
        indicators = [i for i in INDICATORS if i["id"].startswith("marine_")]
        indicators = detect_indicators(geometries, indicators)

    else:
        # include all indicators that are present in area
        indicators = detect_indicators(geometries, INDICATORS)

    for indicator in indicators:
        id = indicator["id"]
        filename = indicators_dir / indicator["filename"]

        values = [e["value"] for e in indicator["values"]]
        bins = np.arange(0, max(values) + 1)
        counts = extract_count_in_geometry(
            filename, shape_mask, window, bins, boundless=True
        )

        # Some indicators exclude 0 values, their counts need to be zeroed out here
        min_value = min(values)
        if min_value > 0:
            counts[range(0, min_value)] = 0

        results["counts"][id] = (
            (counts * cellsize).round(ACRES_PRECISION).astype("float32")
        )

        if indicator.get("continuous"):
            continuous_filename = continuous_indicator_dir / indicator[
                "filename"
            ].replace("_Binned", "")
            mean = extract_zonal_mean(
                continuous_filename, shape_mask, window, boundless=True
            )
            if mean is not None:
                results["means"][id] = mean

    return results


def summarize_by_aoi(shapes, bounds, outside_se_acres):
    """Get results for South Atlantic Conservation Blueprint dataset
    for a given area of interest.

    Parameters
    ----------
    shapes : list-like of geometry objects that provide __geo_interface__
    bounds : list-like of [xmin, ymin, xmax, ymax]
    outside_se_acres : float
        acres of the analysis area that are outside the SE Blueprint region

    Returns
    -------
    dict
        {
            "priorities": [...],
            "legend": [...],
            "analysis_notes": <analysis_notes>,
            "remainder": <acres outside of input>,
            "remainder_percent" <percent of total acres outside input>
        }
    """

    results = extract_by_geometry(shapes, bounds)

    if results is None:
        return None

    total_acres = results["shape_mask"]
    analysis_acres = total_acres - outside_se_acres

    values = pd.DataFrame(INPUTS["sa"]["values"])

    df = values.join(pd.Series(results["sa"], name="acres"))
    df["percent"] = 100 * np.divide(df.acres, total_acres)

    # sort into correct order
    df.sort_values(by=["blueprint", "value"], ascending=False, inplace=True)

    priorities = df[["value", "blueprint", "label", "acres", "percent"]].to_dict(
        orient="records"
    )

    # don't include Not a priority in legend
    legend = df[["label", "color"]].iloc[:-1].to_dict(orient="records")

    remainder = max(analysis_acres - df.acres.sum(), 0)
    remainder = remainder if remainder >= 1 else 0

    return {
        "priorities": priorities,
        "legend": legend,
        "analysis_acres": analysis_acres,
        "total_acres": total_acres,
        "remainder": remainder,
        "remainder_percent": 100 * remainder / total_acres,
    }


def summarize_blueprint_by_geometry(geometries, outfilename, marine=False):
    counts = []
    means = []
    index = []

    for ix, geometry in Bar(
        "Calculating overlap with Blueprint, Corridors, and Indicators",
        max=len(geometries),
    ).iter(geometries.iteritems()):
        zone_results = extract_by_geometry(
            [to_dict(geometry)], bounds=pg.total_bounds(geometry), marine=marine
        )

        if zone_results is None:
            continue

        index.append(ix)
        counts.append(zone_results["counts"])
        means.append(zone_results["means"])

    count_df = pd.DataFrame(counts, index=index)
    mean_df = pd.DataFrame(means, index=index).round()
    mean_df.columns = [f"{c}_avg" for c in mean_df.columns]

    results = count_df[["shape_mask"]].copy()
    results.index.name = "id"

    ### Export the Blueprint, corridors, and indicators
    # each column is an array of counts for each
    for col in count_df.columns.difference(["shape_mask"]):
        s = count_df[col].apply(pd.Series).fillna(0)
        s.columns = [f"{col}_{c}" for c in s.columns]
        results = results.join(s)

    results = results.join(mean_df)

    results.reset_index().to_feather(outfilename)


def summarize_by_huc12(geometries):
    """Summarize by HUC12

    Parameters
    ----------
    geometries : Series of pygeos geometries, indexed by HUC12
    """

    summarize_blueprint_by_geometry(
        geometries, outfilename=huc12_results_filename, marine=False
    )


def summarize_by_marine_block(geometries):
    """Summarize by marine lease block

    Parameters
    ----------
    geometries : Series of pygeos geometries, indexed by marine lease block id
    """

    summarize_blueprint_by_geometry(
        geometries, outfilename=marine_results_filename, marine=True
    )
