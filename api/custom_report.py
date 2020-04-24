"""Create a custom report for a user-uploaded area of interest.

TODO:
* wrap in try / except
"""
import logging
from pathlib import Path
import tempfile

import numpy as np
import pyogrio as pio
import pygeos as pg

from api.errors import DataError
from api.report.map import render_maps
from api.report import create_report
from api.settings import LOGGING_LEVEL, TEMP_DIR
from api.stats import CustomArea
from api.progress import set_progress

from util.pygeos_util import to_crs
from constants import DATA_CRS, GEO_CRS

MAX_DIM = 5  # degrees


log = logging.getLogger(__name__)
log.setLevel(LOGGING_LEVEL)


async def create_custom_report(ctx, zip_filename, dataset, layer, name=""):
    await set_progress(ctx["job_id"], 0)

    path = f"/vsizip/{zip_filename}/{dataset}"

    df = pio.read_dataframe(path, layer=layer, as_pygeos=True)

    geometry = df.geometry
    # Not yet available on ubuntu 18.04
    if pg.geos_version >= (3, 8, 0):
        geometry = pg.make_valid(geometry)

    await set_progress(ctx["job_id"], 5)

    # dissolve
    geometry = np.asarray([pg.union_all(geometry)])

    geo_geometry = to_crs(geometry, df.crs, GEO_CRS)
    bounds = pg.total_bounds(geo_geometry)

    if (bounds[2] - bounds[0]) > MAX_DIM or (bounds[3] - bounds[1]) > MAX_DIM:
        raise DataError(
            "bounds of area of interest are too large.  "
            "Bounds must be < 10 degrees latitude or longitude on edge."
        )

    await set_progress(ctx["job_id"], 10)

    ### calculate results, data must be in DATA_CRS
    print("Calculating results...")
    results = CustomArea(geometry, df.crs, name).get_results()

    if results is None:
        raise DataError("area of interest does not overlap South Atlantic Blueprint")

    if name:
        results["name"] = name

    has_urban = "urban" in results
    has_slr = "slr" in results
    has_ownership = "ownership" in results
    has_protection = "protection" in results

    await set_progress(ctx["job_id"], 25)

    print("Rendering maps...")
    maps, scale = await render_maps(
        bounds,
        geometry=geo_geometry[0],
        indicators=results["indicators"],
        urban=has_urban,
        slr=has_slr,
        ownership=has_ownership,
        protection=has_protection,
    )

    await set_progress(ctx["job_id"], 75)

    results["scale"] = scale

    pdf = create_report(maps=maps, results=results)

    await set_progress(ctx["job_id"], 95)

    fp, name = tempfile.mkstemp(suffix=".pdf", dir=TEMP_DIR)
    with open(fp, "wb") as out:
        out.write(pdf)

    await set_progress(ctx["job_id"], 100)

    log.debug(f"Created PDF at: {name}")

    return name
