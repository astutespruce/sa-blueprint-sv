from pathlib import Path
import pandas as pd

from api.report import create_report
from constants import BLUEPRINT
from util.format import format_number

# Testing: construct results from a HUC12
HUC12 = "030602040601"


data_dir = Path("/Users/bcward/projects/sa-reports/data")


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
unit = huc12.loc[HUC12]

blueprint = pd.read_feather(data_dir / "derived/huc12/blueprint.feather").set_index(
    "huc12"
)
cellsize = 200 * 200 * 0.000247105
result = blueprint.loc[HUC12]
labels = [e["label"] for e in BLUEPRINT]
acres = [format_number(r) for r in (result[1:] * cellsize)]
percents = (100 * result[1:].astype("float32") / result[1:].sum()).astype("uint8")
blueprint_results = list(zip(labels, acres, percents))


params = {
    "aoi_name": unit["name"],
    "aoi_type_label": "subwatershed",
    "blueprint_results": blueprint_results[::-1],
}


pdf = create_report(**params)

with open("/tmp/test_report.pdf", "wb") as out:
    out.write(pdf)
