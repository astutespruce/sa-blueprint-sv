"""Create a custom report for a user-uploaded area of interest.
"""
import logging
import tempfile

import arq
import numpy as np
from pyogrio import read_dataframe
import pygeos as pg

from api.errors import DataError
from api.report.map import render_maps
from api.report import create_report
from api.settings import LOGGING_LEVEL, TEMP_DIR, CUSTOM_REPORT_MAX_ACRES, REDIS
from api.stats import CustomArea
from api.progress import set_progress

from analysis.lib.pygeos_util import to_crs
from analysis.constants import DATA_CRS, GEO_CRS, M2_ACRES

log = logging.getLogger(__name__)
log.setLevel(LOGGING_LEVEL)


async def create_custom_report(ctx, zip_filename, dataset, layer, name=""):
    """Create a Blueprint report for a user-uploaded GIS file contained in a zip.
    Zip must contain either a shapefile or a file geodatabase.

    Parameters
    ----------
    ctx : job context
    zip_filename : str
        full path to zip filename
    dataset : str
        full path to dataset within zip file
    layer : str
        name of layer within dataset
    name : str, optional (default: "")
        Name of area of interest (included in output report)

    Returns
    -------
    str
        path to output file

    Raises
    ------
    DataError
        Raised if bounds are too large or if area of interest doesn't overalap SA region
    """

    errors = []

    await set_progress(ctx["redis"], ctx["job_id"], 0, "Loading data")

    path = f"/vsizip/{zip_filename}/{dataset}"

    df = read_dataframe(path, layer=layer)

    geometry = pg.make_valid(df.geometry.values.data)

    await set_progress(ctx["redis"], ctx["job_id"], 5, "Preparing area of interest")

    # dissolve
    geometry = np.asarray([pg.union_all(geometry)])

    geo_geometry = to_crs(geometry, df.crs, GEO_CRS)
    bounds = pg.total_bounds(geo_geometry)

    # estimate area
    extent_area = (
        pg.area(pg.box(*pg.total_bounds(to_crs(geometry, df.crs, DATA_CRS)))) * M2_ACRES
    )
    if extent_area >= CUSTOM_REPORT_MAX_ACRES:
        raise DataError(
            f"The bounding box of your area of interest is too large ({extent_area:,.0f} acres), it must be < {CUSTOM_REPORT_MAX_ACRES:,.0f} acres."
        )

    await set_progress(
        ctx["redis"], ctx["job_id"], 10, "Calculating results (this might take a while)"
    )

    ### calculate results, data must be in DATA_CRS
    print("Calculating results...")
    results = CustomArea(geometry, df.crs, name).get_results()

    if results is None:
        raise DataError("area of interest does not overlap South Atlantic Blueprint")

    if name:
        results["name"] = name

    # only include urban up to 2060
    has_urban = "proj_urban" in results and results["proj_urban"][4] > 0
    has_slr = "slr" in results
    has_ownership = "ownership" in results
    has_protection = "protection" in results

    await set_progress(
        ctx["redis"], ctx["job_id"], 25, "Creating maps (this might take a while)"
    )

    print("Rendering maps...")
    maps, scale, map_errors = await render_maps(
        bounds,
        geometry=geo_geometry[0],
        indicators=results["indicators"],
        urban=has_urban,
        slr=has_slr,
        ownership=has_ownership,
        protection=has_protection,
    )

    if map_errors:
        log.error(f"Map rendering errors: {map_errors}")
        if "basemap" in map_errors:
            errors.append("Error creating basemap for all maps")

        if "aoi" in map_errors:
            errors.append("Error rendering area of interest on maps")

        if set(map_errors.keys()).difference(["basemap", "aoi"]):
            errors.append("Error creating one or more maps")

    await set_progress(
        ctx["redis"],
        ctx["job_id"],
        75,
        "Creating PDF (this might take a while)",
        errors=errors,
    )

    results["scale"] = scale

    pdf = create_report(maps=maps, results=results)

    await set_progress(ctx["redis"], ctx["job_id"], 95, "Nearly done", errors=errors)

    fp, name = tempfile.mkstemp(suffix=".pdf", dir=TEMP_DIR)
    with open(fp, "wb") as out:
        out.write(pdf)

    await set_progress(ctx["redis"], ctx["job_id"], 100, "All done!", errors=errors)

    log.debug(f"Created PDF at: {name}")

    return name, errors
