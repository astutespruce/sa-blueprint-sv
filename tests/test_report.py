from base64 import b64decode, b64encode
import os
from pathlib import Path

import pandas as pd
import numpy as np
import pygeos as pg
from pyogrio import read_dataframe

from api.report import create_report
from api.map import render_maps
from constants import BLUEPRINT, INDICATORS, GEO_CRS, DATA_CRS
from api.map import get_scale, WIDTH as map_width
from util.format import format_number
from api.summary_units import SummaryUnits
from api.stats import calculate_results
from util.pygeos_util import to_crs


# if True, cache maps if not previously created, then reuse
CACHE_MAPS = True


def write_cache(maps, path):
    if not path.exists():
        os.makedirs(path)

    for name, data in maps.items():
        with open(path / f"{name}.png", "wb") as out:
            out.write(b64decode(data))


def read_cache(path):
    if not path.exists():
        # cache miss
        return None

    maps = {}
    for filename in path.glob("*.png"):
        name = filename.stem
        maps[name] = b64encode(open(filename, "rb").read()).decode("utf-8")

    print("CACHE: loaded maps from cache")

    return maps


### Create reports for an AOI
aois = [
    # {"name": "Rasor Forest Legacy Tract", "path": "Razor"},
    # {"name": "Groton Plantation", "path": "Groton_all"},
    # {
    #     "name": "80-mile sourcing radius for Enviva’s Hamlet, NC plant",
    #     "path": "Enviva_Hamlet_80_mile_sourcing_radius",
    # },
    # TODO: invalid CRS
    # {"name": "Fort Mill Town Limits", "path": "Fort_Mill_townlimits"},
    # TODO: doesn't overlap, need to handle
    # {"name": "Green River Proposed Boundary", "path": "GreenRiver_ProposedBoundary"},
    # {"name": "FY18 LWCF Tract", "path": "FY18_LWCF_Tract"},
    {"name": "ACF", "path": "ACF_area"}
]


for aoi in aois:
    name = aoi["name"]
    path = aoi["path"]
    print(f"Creating report for {name}...")

    ### Write maps for an aoi
    out_dir = Path("/tmp/aoi") / path
    if not out_dir.exists():
        os.makedirs(out_dir)

    cache_dir = out_dir / "maps"

    df = read_dataframe(f"data/aoi/{path}.shp", as_pygeos=True)
    geometry = pg.make_valid(df.geometry)

    # dissolve
    geometry = np.asarray([pg.union_all(geometry)])

    ### calculate results, data must be in DATA_CRS
    print("Calculating results...")
    analysis_geom = to_crs(geometry, df.crs, DATA_CRS)
    results = calculate_results(analysis_geom)
    results["scale"] = get_scale(pg.total_bounds(analysis_geom), map_width)
    results["name"] = name

    maps = None
    if CACHE_MAPS:
        maps = read_cache(cache_dir)

    if not maps:
        print("Rendering maps...")
        geometry = to_crs(geometry, df.crs, GEO_CRS)
        bounds = pg.total_bounds(geometry)

        has_urban = "urban" in results
        has_slr = "slr" in results

        maps = render_maps(
            bounds,
            geometry=geometry[0],
            indicators=results["indicators"],
            urban=has_urban,
            slr=has_slr,
        )

        if CACHE_MAPS:
            write_cache(maps, cache_dir)

    pdf = create_report(maps=maps, results=results)

    with open(out_dir / f"{path}_report.pdf", "wb") as out:
        out.write(pdf)


### Create reports for summary units
# ids = {
#     "huc12": [
#         "030602040601",
#         "030601030510",
#         "031501040301",
#         "030102020505"
#     ],
#     "marine_blocks": ["NI18-07-6210"]
# }


# for summary_type in ids:
#     units = SummaryUnits(summary_type)

#     for id in ids[summary_type]:
#         print(f"Creating report for for {id}...")

#         out_dir = Path(f"/tmp/{id}")
#         cache_dir = out_dir / "maps"

#         if not out_dir.exists():
#             os.makedirs(out_dir)

#         # Fetch results
#         results = units.get_results(id)

#         maps = None
#         if CACHE_MAPS:
#             maps = read_cache(cache_dir)

#         if not maps:
#             print("Rendering maps...")
#             maps = render_maps(
#                 results["bounds"], summary_unit_id=id, indicators=results["indicators"]
#             )

#             if CACHE_MAPS:
#                 write_cache(maps, cache_dir)

#         pdf = create_report(maps=maps, results=results)

#         with open(out_dir / f"{id}_report.pdf", "wb") as out:
#             out.write(pdf)
