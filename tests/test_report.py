import asyncio
from base64 import b64decode, b64encode
import json
import os
from pathlib import Path
from time import time

import pandas as pd
import numpy as np
import pygeos as pg
from pyogrio.geopandas import read_dataframe

from api.report import create_report
from api.report.map import render_maps
from analysis.constants import BLUEPRINT, INDICATORS, GEO_CRS, DATA_CRS, M2_ACRES
from api.report.format import format_number
from api.stats import SummaryUnits, CustomArea
from analysis.lib.pygeos_util import to_crs


# if True, cache maps if not previously created, then reuse
CACHE_MAPS = False  # FIXME


def write_cache(maps, scale, path):
    if not path.exists():
        os.makedirs(path)

    for name, data in maps.items():
        if data is not None:
            with open(path / f"{name}.png", "wb") as out:
                out.write(b64decode(data))

    with open(path / f"scale.json", "w") as out:
        out.write(json.dumps(scale))


def read_cache(path):
    if not path.exists():
        # cache miss
        return None, None

    maps = {}
    for filename in path.glob("*.png"):
        name = filename.stem
        maps[name] = b64encode(open(filename, "rb").read()).decode("utf-8")

    scale = json.loads(open(path / "scale.json").read())

    print("CACHE: loaded maps from cache")

    return maps, scale


### Create reports for an AOI
aois = [
    # {
    #     "name": "NWFL Sentinel Landscapes Geography",
    #     "path": "NWFL_SentinelLandscapesGeography_20210812",
    # }
    # {"name": "CFLCP 3 mile buffer", "path": "CFLCP_Buffer_3mi"}
    # {"name": "Florida 5 Star County Boundary", "path": "FL_5StarCounty_Boundary"},
    # {"name": "Dell Murphy wetlands", "path": "Dell Murphy wetlands"}
    # {"name": "Cumberland Plateau Focus Area", "path": "NFWF_Cumberland_Fund_TN"}
    # {"name": "Pied_LowerBroad", "path": "Pied_LowerBroad"},
    # {"name": "Pied_Saluda", "path": "Pied_Saluda"},
    # {"name": "UCP: Lower Pee Dee", "path": "UCP_LowerPeeDee"},
    # {"name": "LCP: Broad", "path": "LCP_Broad"},
    # {"name": "LCP: Black River", "path": "LCP_BlackRiver"},
    # {
    #     "name": "Congaree Creek Assemblage tracts",
    #     "path": "CongareeCreekAssemblageTracts",
    # },
    # {"name": "Alderman-Shaw tract", "path": "Alderman-ShawTract"},
    # {"name": "Town of Van Wyck planning area", "path": "Planning_Area"},
    # {"name": "Gainesville area", "path": "POLYGON"},
    # {"name": "Rasor Forest Legacy Tract", "path": "Razor"},
    # {"name": "Groton Plantation", "path": "Groton_all"},
    # {"name": "Fort Mill Town Limits", "path": "Fort_Mill_townlimits"},
    # {"name": "FY18 LWCF Tract", "path": "FY18_LWCF_Tract"},
    # # # TODO: handle correctly
    # # {"name": "Green River Proposed Boundary", "path": "GreenRiver_ProposedBoundary"},
    # # # Big areas:
    # {"name": "ACF", "path": "ACF_area"},  # 140s
    # {
    #     "name": "80-mile sourcing radius for Enviva’s Hamlet, NC plant",
    #     "path": "Enviva_Hamlet_80_mile_sourcing_radius",
    # },  # 112s
    # {"name": "North Carolina", "path": "NC"},  # 330s
    # {"name": "South Atlantic Region", "path": "SA_boundary"},
]


for aoi in aois:
    name = aoi["name"]
    path = aoi["path"]
    print(f"Creating report for {name}...")

    start = time()
    df = read_dataframe(f"examples/{path}.shp", columns=[])
    geometry = pg.make_valid(df.geometry.values.data)

    # dissolve
    geometry = np.asarray([pg.union_all(geometry)])

    extent_area = (
        pg.area(pg.box(*pg.total_bounds(to_crs(geometry, df.crs, DATA_CRS)))) * M2_ACRES
    )

    print(f"Analysis extent: {extent_area:,.0f}")

    ### calculate results, data must be in DATA_CRS
    print("Calculating results...")
    results = CustomArea(geometry, df.crs, name=name).get_results()

    if results is None:
        print(f"AOI: {path} does not overlap Blueprint")
        continue

    out_dir = Path("/tmp/aoi") / path
    if not out_dir.exists():
        os.makedirs(out_dir)

    cache_dir = out_dir / "maps"

    maps = None
    scale = None
    if CACHE_MAPS:
        maps, scale = read_cache(cache_dir)

    if not maps:
        print("Rendering maps...")
        geometry = to_crs(geometry, df.crs, GEO_CRS)
        bounds = pg.total_bounds(geometry)

        # only include urban up to 2060
        has_urban = "proj_urban" in results and results["proj_urban"][4] > 0
        has_slr = "slr" in results
        has_ownership = "ownership" in results
        has_protection = "protection" in results

        task = render_maps(
            bounds,
            geometry=geometry[0],
            indicators=results["indicators"],
            urban=has_urban,
            slr=has_slr,
            ownership=has_ownership,
            protection=has_protection,
        )

        maps, scale, errors = asyncio.run(task)

        if errors:
            print("Errors", errors)

        if CACHE_MAPS:
            write_cache(maps, scale, cache_dir)

    results["scale"] = scale

    pdf = create_report(maps=maps, results=results)

    with open(out_dir / f"{path}_report.pdf", "wb") as out:
        out.write(pdf)

    print("Elapsed {:.2f}s".format(time() - start))


### Create reports for summary units
ids = {
    "huc12": [
        # "030601100303",
        # "030601030404",  # has no protected areas
        # # "031200030902"
        # "031501041004",  # partial overlap with SA raster inputs
        "030502060308",
        "030601070305",
        # "030300050503",  # multiple PARCA
        #     #     # "030602040101",
        #     #     # "030602040601",
        #     #     #     "030601030510",
        #     #     # "031501040301",
        #     #     #     "030102020505",
        #     #     #     "030203020403",
        #     #     #     "030203020404",
        #     #     #     "030203020405",
    ],
    # "marine_blocks": ["NI18-07-6210"],
}


for summary_type in ids:
    units = SummaryUnits(summary_type)

    for id in ids[summary_type]:
        print(f"Creating report for for {id}...")

        out_dir = Path(f"/tmp/{id}")
        cache_dir = out_dir / "maps"

        if not out_dir.exists():
            os.makedirs(out_dir)

        # Fetch results
        results = units.get_results(id)

        # only include urban up to 2060
        has_urban = "proj_urban" in results and results["proj_urban"][4] > 0
        has_slr = "slr" in results
        has_ownership = "ownership" in results
        has_protection = "protection" in results

        maps = None
        if CACHE_MAPS:
            maps, scale = read_cache(cache_dir)

        if not maps:
            print("Rendering maps...")
            task = render_maps(
                results["bounds"],
                summary_unit_id=id,
                indicators=results["indicators"],
                urban=has_urban,
                slr=has_slr,
                ownership=has_ownership,
                protection=has_protection,
            )
            maps, scale, errors = asyncio.run(task)

            if errors:
                print("Errors", errors)

            if CACHE_MAPS:
                write_cache(maps, scale, cache_dir)

        results["scale"] = scale

        pdf = create_report(maps=maps, results=results)

        with open(out_dir / f"{id}_report.pdf", "wb") as out:
            out.write(pdf)
