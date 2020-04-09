"""Create a custom report for a user-uploaded area of interest.

TODO:
* wrap in try / except
"""
from pathlib import Path

import numpy as np
import pyogrio as pio
import pygeos as pg

from api.report.map import render_maps
from api.report import create_report
from api.stats import CustomArea

from util.pygeos_util import to_crs
from constants import DATA_CRS, GEO_CRS


async def create_custom_report(zip_filename, dataset, layer, name):
    path = f"/vsizip/{zip_filename}/{dataset}"

    df = pio.read_dataframe(path, layer=layer, as_pygeos=True)
    geometry = pg.make_valid(df.geometry)

    # dissolve
    geometry = np.asarray([pg.union_all(geometry)])

    ### calculate results, data must be in DATA_CRS
    print("Calculating results...")
    results = CustomArea(geometry, df.crs, name).get_results()

    if results is None:
        raise ValueError("Area of interest does not overlap South Atlantic Blueprint")

    print("Rendering maps...")
    geometry = to_crs(geometry, df.crs, GEO_CRS)
    bounds = pg.total_bounds(geometry)

    has_urban = "urban" in results
    has_slr = "slr" in results

    maps, scale = await render_maps(
        bounds,
        geometry=geometry[0],
        indicators=results["indicators"],
        urban=has_urban,
        slr=has_slr,
    )

    results["scale"] = scale

    return create_report(maps=maps, results=results)
