from pathlib import Path
import pandas as pd

from geofeather.pygeos import from_geofeather
import pygeos as pg

from api.report import create_report
from api.map import render_maps
from constants import BLUEPRINT, INDICATORS
from util.format import format_number


# Testing: construct results from a HUC12
UNIT_ID = "030602040601"


data_dir = Path("/Users/bcward/projects/sa-reports/data")


print("Rendering maps...")
df = from_geofeather(data_dir / "summary_units/units.feather").set_index("id")
geometry = df.loc[UNIT_ID].geometry
bounds = pg.total_bounds(geometry)
maps = render_maps(
    bounds, summary_unit_id=UNIT_ID, indicators=[i["id"] for i in INDICATORS[:8]]
)

print("Fetching results...")
huc12 = pd.read_feather(
    data_dir / "summary_units/huc12.feather",
    columns=[
        "HUC12",
        "name",
        "Justification",
        "PARCA",
        "TNC",
        "EPA",
        "ACJV",
        "NBCI",
        "Alabama",
        "Florida",
        "NorthCarolina",
        "Virginia",
        "Georgia",
    ],
).set_index("HUC12")
unit = huc12.loc[UNIT_ID]

blueprint = pd.read_feather(data_dir / "derived/huc12/blueprint.feather").set_index(
    "huc12"
)
cellsize = 200 * 200 * 0.000247105
result = blueprint.loc[UNIT_ID]
labels = [e["label"] for e in BLUEPRINT]
acres = [format_number(r) for r in (result[1:] * cellsize)]
percents = (100 * result[1:].astype("float32") / result[1:].sum()).astype("uint8")
blueprint_results = list(zip(labels, acres, percents))


params = {
    "aoi_name": unit["name"],
    "aoi_type_label": "subwatershed",
    "maps": maps,
    "blueprint_results": blueprint_results[::-1],
}


pdf = create_report(**params)

with open("/tmp/test_report.pdf", "wb") as out:
    out.write(pdf)
