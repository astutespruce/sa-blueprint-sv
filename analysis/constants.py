from pathlib import Path
from collections import OrderedDict
import json

# Set to True to output intermediate rasters for validation (uncomment in map.raster module)
# Set to True to output /tmp/test.html for reports
DEBUG = False

DATA_CRS = "EPSG:5070"
GEO_CRS = "EPSG:4326"
MAP_CRS = "EPSG:3857"

ACRES_PRECISION = 1
# meters to acres
M2_ACRES = 0.000247105
M_MILES = 0.000621371

# 32 is OK for regional level maps; 16 is more typical for big areas like ACF
OVERVIEW_FACTORS = [2, 4, 8, 16, 32]

json_dir = Path("constants")

# indexed by BP value
BLUEPRINT = json.loads(open(json_dir / "blueprint.json").read())
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

CORRIDORS_COLORS = {
    i: entry["color"] for i, entry in enumerate(CORRIDORS) if "color" in entry
}

INDICATOR_INDEX = OrderedDict({indicator["id"]: indicator for indicator in INDICATORS})
ECOSYSTEM_INDEX = {ecosystem["id"]: ecosystem for ecosystem in ECOSYSTEMS}


URBAN_YEARS = [2020, 2030, 2040, 2050, 2060, 2070, 2080, 2090, 2100]

URBAN_LEGEND = [
    None,  # spacer; not actually displayed
    {"label": "Urban in 2009", "color": "#696969"},
    {"label": "< 2.5% probability", "color": "#FFEBD6"},
    {"label": "5%", "color": "#F8D7BE"},
    {"label": "10%", "color": "#F2C2A5"},
    {"label": "20%", "color": "#EBAE8D"},
    {"label": "30%", "color": "#E79D7D"},
    {"label": "40%", "color": "#E28C6D"},
    {"label": "50%", "color": "#DE7B5D"},
    {"label": "60%", "color": "#DA694F"},
    {"label": "70%", "color": "#D55740"},
    {"label": "80%", "color": "#D14532"},
    {"label": "90%", "color": "#CE3628"},
    {"label": "95%", "color": "#CB281E"},
    {"label": "97.5%", "color": "#C71914"},
    {"label": "> 97.5% probability", "color": "#C40A0A"},
]


SLR_LEGEND = [
    {"label": "Current (already flooded at high tide)", "color": "#002673"},
    {"label": "1 foot of SLR", "color": "#003BA1"},
    {"label": "2 feet of SLR", "color": "#0053D0"},
    {"label": "3 feet of SLR", "color": "#006EFF"},
    {"label": "4 feet of SLR", "color": "#40A0FF"},
    {"label": "5 feet of SLR", "color": "#80C9FF"},
    {"label": "6 feet of SLR", "color": "#BFE9FF"},
]
