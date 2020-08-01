"""
Render tiles to mbtiles files.

NOTE: this is sensitive to the version of GDAL / rasterio; otherwise it raises errors about negative dimensions.
This appears to work properly on locally-built rasterio / GDAL.

Low resolution version of Blueprint created using gdal_translate:
gdal_translate -tr 240 240 blueprint_2020.tif blueprint_2020_240.tif

Creating blueprint tiles takes about 3 hours.
"""


from pathlib import Path

from tilecutter.mbtiles import render_tif_to_mbtiles
from pymbtiles.ops import extend
from pymbtiles import MBtiles

from analysis.constants import BLUEPRINT


src_dir = Path("data/inputs")
tile_dir = Path("tiles")
tmp_dir = Path("/tmp")

tileset_filename = tile_dir / "blueprint_2020.mbtiles"
lowres_filename = tmp_dir / "blueprint_2020_lowres.mbtiles"

### Render Blueprint
colormap = {i + 1: entry["color"] for i, entry in enumerate(BLUEPRINT[1:])}


# Render low resolution version for lower zooms
print("Rendering low resolution tiles...")
render_tif_to_mbtiles(
    src_dir / "blueprint_2020_240.tif",
    lowres_filename,
    colormap=colormap,
    min_zoom=0,
    max_zoom=4,
    tile_size=512,
    metadata={
        "name": "South Atlantic Conservation Blueprint 2020",
        "description": "South Atlantic Conservation Blueprint 2020",
        "attribution": "South Atlantic Conservation Blueprint 2020",
    },
)

# Render original 30m data
# TODO: split this into multiple batches and multiprocess?

print("Rendering high resolution tiles...")
render_tif_to_mbtiles(
    src_dir / "blueprint_2020.tif",
    tileset_filename,
    colormap={i + 1: entry["color"] for i, entry in enumerate(BLUEPRINT[1:])},
    min_zoom=5,
    max_zoom=15,
    # max_zoom=15,
    tile_size=512,
    metadata={
        "name": "South Atlantic Conservation Blueprint 2020",
        "description": "South Atlantic Conservation Blueprint 2020",
        "attribution": "South Atlantic Conservation Blueprint 2020",
    },
)

# Merge into single tileset
print("Merging tilesets...")
extend(lowres_filename, tileset_filename)

# update the metadata
with MBtiles(tileset_filename, "r+") as tileset:
    tileset.meta["minzoom"] = 0

