"""
Render tiles to mbtiles files, zooms 0-15

NOTE: this is sensitive to the version of GDAL / rasterio; otherwise it raises errors about negative dimensions.
This appears to work properly on locally-built rasterio / GDAL.

Creating blueprint tiles takes about 3 hours sequentially.  Zoom 15 takes 2 hours.
This can be done more quickly (total time) in batches and merge them back later.
"""

from time import time
from pathlib import Path

from tilecutter.mbtiles import render_tif_to_mbtiles
from pymbtiles.ops import union, extend
from pymbtiles import MBtiles

from analysis.constants import BLUEPRINT


src_dir = Path("data/inputs")
tile_dir = Path("tiles")
tmp_dir = Path("/tmp")


blueprint_filename = src_dir / "blueprint2020.tif"
tileset_filename = tile_dir / "blueprint_2020.mbtiles"


### Render Blueprint sequentially
start = time()
render_tif_to_mbtiles(
    src_dir / "blueprint2020.tif",
    tileset_filename,
    colormap={i + 1: entry["color"] for i, entry in enumerate(BLUEPRINT[1:])},
    min_zoom=0,
    max_zoom=15,
    tile_size=512,
    metadata={
        "name": "South Atlantic Conservation Blueprint 2020",
        "description": "South Atlantic Conservation Blueprint 2020",
        "attribution": "South Atlantic Conservation Blueprint 2020",
    },
)
print("Tiles done in {:.2f} min".format((time() - start) / 60.0))


# ### Render Blueprint in batches
# # break into batches for zoom ranges
# # z14: about 36min
# # z15: about 2 hours
# batches = [[0, 13], [14, 14], [15, 15]]

# # change this manually in separate terminal windows
# batch = batches[0]

# min_zoom, max_zoom = batch
# print(f"Rendering tiles: {min_zoom} - {max_zoom}...")
# start = time()

# outfilename = tmp_dir / f"blueprint2020_{min_zoom}_{max_zoom}.mbtiles"
# render_tif_to_mbtiles(
#     src_dir / "blueprint2020.tif",
#     outfilename,
#     colormap={i + 1: entry["color"] for i, entry in enumerate(BLUEPRINT[1:])},
#     min_zoom=min_zoom,
#     max_zoom=max_zoom,
#     tile_size=512,
#     metadata={
#         "name": "South Atlantic Conservation Blueprint 2020",
#         "description": "South Atlantic Conservation Blueprint 2020",
#         "attribution": "South Atlantic Conservation Blueprint 2020",
#     },
# )
# print("Tiles done in {:.2f} min".format((time() - start) / 60.0))


### Merge into single tileset (about 1 min)
# print("Merging tilesets...")
# start = time()
# filenames = [
#     tmp_dir / f"blueprint2020_{min_zoom}_{max_zoom}.mbtiles"
#     for min_zoom, max_zoom in batches
# ]
# # flip the order so we merge into the bigger ones
# filenames.reverse()

# # union the first 2
# union(filenames[0], filenames[1], tileset_filename)

# # extend in the rest
# for filename in filenames[2:]:
#     extend(filename, tileset_filename)

# # update the metadata
# with MBtiles(tileset_filename, "r+") as tileset:
#     tileset.meta["minzoom"] = batches[0][0]
#     tileset.meta["maxzoom"] = batches[-1][-1]


# print("All done in {:.2f}s".format(time() - start)

