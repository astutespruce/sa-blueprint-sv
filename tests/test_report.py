from base64 import b64decode, b64encode
import os
from pathlib import Path

import pandas as pd

from api.report import create_report
from api.map import render_maps
from constants import BLUEPRINT, INDICATORS
from util.format import format_number
from api.summary_units import SummaryUnits


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
        # maps[name] = open(filename, "rb").read()
    print("CACHE: loaded maps from cache")

    return maps


ids = {
    "huc12": [
        # "030602040601",
        "030601030510",
        # "031501040301",
        # "030102020505"
    ],
    # "marine_blocks": ["NI18-07-6210"]
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

        maps = None
        if CACHE_MAPS:
            maps = read_cache(cache_dir)

        if not maps:
            print("Rendering maps...")
            maps = render_maps(
                results["bounds"], summary_unit_id=id, indicators=results["indicators"]
            )

            if CACHE_MAPS:
                write_cache(maps, cache_dir)

        pdf = create_report(maps=maps, results=results)

        with open(out_dir / f"{id}_report.pdf", "wb") as out:
            out.write(pdf)
