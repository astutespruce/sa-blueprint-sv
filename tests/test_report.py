from pathlib import Path
import pandas as pd


from api.report import create_report
from api.map import render_maps
from constants import BLUEPRINT, INDICATORS
from util.format import format_number
from api.summary_units import SummaryUnits


# Testing: construct results from a HUC12
id = "030602040601"
huc12 = SummaryUnits("huc12")
results = huc12.get_results(id)


data_dir = Path("data")


print("Rendering maps...")

# maps = render_maps(
#     results["bounds"], summary_unit_id=id, indicators=results["indicators"]
# )

# FIXME
maps = []

pdf = create_report(maps=maps, results=results)

with open("/tmp/test_report.pdf", "wb") as out:
    out.write(pdf)
