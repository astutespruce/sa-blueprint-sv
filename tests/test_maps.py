from base64 import b64decode
import os
from pathlib import Path
import json

from geofeather.pygeos import from_geofeather
import geopandas as gp
import pygeos as pg

from constants import BLUEPRINT_COLORS, DATA_CRS, MAP_CRS, GEO_CRS, INDICATORS
from api.map.util import to_geojson, pad_bounds, get_center

from api.map import get_maps

# HUC12
UNIT_ID = "030602040601"


# ### Write maps for an aoi
# out_dir = Path("/tmp/aoi")
# if not out_dir.exists():
#     os.makedirs(out_dir)

# src_dir = Path("data")
# # filename = "Razor_prj.shp"
# # filename = "ACF_prj.shp"
# filename = "Groton_prj.shp"
# geometry = gp.read_file(f"data/aoi/{filename}").geometry

# geometry = geometry.to_crs("EPSG:4326")
# bounds = geometry.total_bounds
# geojson = to_geojson(geometry)

# maps = get_maps(bounds, geojson=geojson, indicators=[i["id"] for i in INDICATORS[:8]])
# for name, data in maps.items():
#     with open(out_dir / f"{name}.png", "wb") as out:
#         out.write(b64decode(data))


### Write maps for a summary unit
out_dir = Path("/tmp/summary_unit")
if not out_dir.exists():
    os.makedirs(out_dir)

df = from_geofeather("data/summary_units/units.feather").set_index("id")
geometry = df.loc[UNIT_ID].geometry
bounds = pg.total_bounds(geometry)

maps = get_maps(
    bounds, summary_unit_id=UNIT_ID, indicators=[i["id"] for i in INDICATORS[:8]]
)

for name, data in maps.items():
    with open(out_dir / f"{name}.png", "wb") as out:
        out.write(b64decode(data))

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
