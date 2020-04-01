from base64 import b64decode
import os
from pathlib import Path
import json

from geofeather.pygeos import from_geofeather
import geopandas as gp
import pygeos as pg

from constants import BLUEPRINT_COLORS, DATA_CRS, MAP_CRS, GEO_CRS, INDICATORS
from api.map.util import to_geojson
from api.map import render_maps
from api.summary_units import SummaryUnits


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

# maps = render_maps(bounds, geojson=geojson, indicators=[i["id"] for i in INDICATORS[:8]])
# for name, data in maps.items():
#     with open(out_dir / f"{name}.png", "wb") as out:
#         out.write(b64decode(data))


### Write maps for a summary unit
# HUC12
id = "030602040601"
huc12 = SummaryUnits("huc12")
results = huc12.get_results(id)

has_urban = "urban" in results
has_slr = "slr" in results

out_dir = Path(f"/tmp/{id}/maps")
if not out_dir.exists():
    os.makedirs(out_dir)

maps = render_maps(
    results["bounds"],
    summary_unit_id=id,
    indicators=results["indicators"],
    urban=has_urban,
    slr=has_slr,
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
