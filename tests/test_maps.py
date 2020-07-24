from base64 import b64decode
import os
from pathlib import Path
import json

import asyncio
import numpy as np
import pygeos as pg
from pyogrio.geopandas import read_dataframe

from constants import BLUEPRINT_COLORS, DATA_CRS, MAP_CRS, GEO_CRS, DATA_CRS, INDICATORS

from util.pygeos_util import to_crs, to_dict
from api.report.map import render_maps
from api.stats import SummaryUnits, CustomArea


aoi_names = ["Razor", "Groton_all"]
# aoi_names = ["ACF_area"]
# aoi_names = ["NC"]

for aoi_name in aoi_names:
    print(f"Making maps for {aoi_name}...")

    ### Write maps for an aoi
    out_dir = Path("/tmp/aoi") / aoi_name / "maps"
    if not out_dir.exists():
        os.makedirs(out_dir)

    df = read_dataframe(f"data/aoi/{aoi_name}.shp")
    geometry = pg.make_valid(df.geometry.values.data)

    # dissolve
    geometry = np.asarray([pg.union_all(geometry)])

    print("Calculating results...")
    results = CustomArea(geometry, df.crs, name="Test").get_results()

    ### Convert to WGS84 for mapping
    geometry = to_crs(geometry, df.crs, GEO_CRS)
    bounds = pg.total_bounds(geometry)

    has_urban = "urban" in results
    has_slr = "slr" in results
    has_ownership = "ownership" in results
    has_protection = "protection" in results

    print("Creating maps...")

    task = render_maps(
        bounds,
        geometry=geometry[0],
        indicators=results["indicators"],
        urban=has_urban,
        slr=has_slr,
        ownership=has_ownership,
        protection=has_protection,
    )

    maps, scale = asyncio.run(task)

    for name, data in maps.items():
        if data is not None:
            with open(out_dir / f"{name}.png", "wb") as out:
                out.write(b64decode(data))

    with open(out_dir / f"scale.json", "w") as out:
        out.write(json.dumps(scale))


### Write maps for a summary unit

ids = {
    # "huc12": [
    #     "030602040601",
    #     # "030601030510", "031501040301", "030102020505"
    # ],
    # "marine_blocks": ["NI18-07-6210"],
}


for summary_type in ids:
    units = SummaryUnits(summary_type)

    for id in ids[summary_type]:
        print(f"Making maps for {id}...")

        results = units.get_results(id)

        has_urban = "urban" in results
        has_slr = "slr" in results
        has_ownership = "ownership" in results
        has_protection = "protection" in results

        out_dir = Path(f"/tmp/{id}/maps")
        if not out_dir.exists():
            os.makedirs(out_dir)

        task = render_maps(
            results["bounds"],
            summary_unit_id=id,
            indicators=results["indicators"],
            urban=has_urban,
            slr=has_slr,
            ownership=has_ownership,
            protection=has_protection,
        )

        maps, scale = asyncio.run(task)

        for name, data in maps.items():
            if data is not None:
                with open(out_dir / f"{name}.png", "wb") as out:
                    out.write(b64decode(data))

        with open(out_dir / f"scale.json", "w") as out:
            out.write(json.dumps(scale))

### Write bounds as a polygon for display on map (DEBUG)
# xmin, ymin, xmax, ymax = bounds
# bounds_geojson = {
#     "type": "Polygon",
#     "coordinates": [
#         [[xmin, ymin], [xmin, ymax], [xmax, ymax], [xmax, ymin], [xmin, ymin]]
#     ],
# }
# with open("/tmp/bounds.json", "w") as out:
#     out.write(json.dumps(bounds_geojson))
