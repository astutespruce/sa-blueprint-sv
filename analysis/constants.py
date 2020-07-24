from pathlib import Path
from collections import OrderedDict
import json

# Set to True to output intermediate rasters for validation (uncomment in map.raster module)
# Set to True to output /tmp/test.html for reports
# FIXME:
DEBUG = True

DATA_CRS = "EPSG:5070"
GEO_CRS = "EPSG:4326"
MAP_CRS = "EPSG:3857"

ACRES_PRECISION = 1
# meters to acres
M2_ACRES = 0.000247105
M_MILES = 0.000621371


json_dir = Path("ui/config")


# indexed by BP value
BLUEPRINT = json.loads(open(json_dir / "blueprint.json").read())
ECOSYSTEM_GROUPS = json.loads(open(json_dir / "ecosystem_groups.json").read())
ECOSYSTEMS = json.loads(open(json_dir / "ecosystems.json").read())
INDICATORS = json.loads(open(json_dir / "indicators.json").read())
CORRIDORS = json.loads(open(json_dir / "corridors.json").read())
OWNERSHIP = OrderedDict(
    {e["value"]: e for e in json.loads(open(json_dir / "ownership.json").read())}
)
PROTECTION = OrderedDict(
    {e["value"]: e for e in json.loads(open(json_dir / "protection.json").read())}
)


BLUEPRINT_COLORS = {
    i: entry["color"]
    for i, entry in enumerate(BLUEPRINT)
    if "color" in entry and entry["value"] > 0
}

INDICATOR_INDEX = OrderedDict({indicator["id"]: indicator for indicator in INDICATORS})
ECOSYSTEM_INDEX = {ecosystem["id"]: ecosystem for ecosystem in ECOSYSTEMS}


URBAN_YEARS = [2020, 2030, 2040, 2050, 2060, 2070, 2080, 2090, 2100]

URBAN_LEGEND = [
    None,  # spacer; not actually displayed
    {"label": "Urban in 2009", "color": "#333333"},
    {"label": "< 2.5% probability", "color": "#FFBFBA"},
    {"label": "5%", "color": "#FFB1A8"},
    {"label": "10%", "color": "#FFA496"},
    {"label": "20%", "color": "#FF9787"},
    {"label": "30%", "color": "#FC8B76"},
    {"label": "40%", "color": "#FC806B"},
    {"label": "50%", "color": "#FA735A"},
    {"label": "60%", "color": "#F5654B"},
    {"label": "70%", "color": "#F25740"},
    {"label": "80%", "color": "#F04D35"},
    {"label": "90%", "color": "#EB402A"},
    {"label": "95%", "color": "#E5311B"},
    {"label": "97.5%", "color": "#E12114"},
    {"label": "> 97.5% probability", "color": "#DB0000"},
]


SLR_LEGEND = [
    {"label": "< 1 foot", "color": "#2B00A1"},
    {"label": "1", "color": "#403EB9"},
    {"label": "2", "color": "#4567CF"},
    {"label": "3", "color": "#4495E5"},
    {"label": "4", "color": "#74B0EB"},
    {"label": "5", "color": "#94CBEF"},
    {"label": "≥ 6 feet", "color": "#C0F0F3"},
]
