from time import time
from pathlib import Path
import json

import pandas as pd
from tilecutter.mbtiles import tif_to_mbtiles
from tilecutter.png import to_smallest_png


src_dir = Path("data/for_tiles")
out_dir = Path("tiles")


# tile_size = 128
tile_size = 512
min_zoom = 4
max_zoom = 10
# max_zoom = 14  # NOTE: z14 takes 2+ hours per tileset

# IMPORTANT: need to force tile renderer to always use either paletted RGB or
# full RGB; cannot use grayscale (L) or it won't be decoded properly
renderer = lambda arr: to_smallest_png(arr, image_type="P" if arr.max() < 255 else "RGB")


df = pd.read_feather(src_dir / "encoding.feather")

start = time()


for group in sorted(df.group.unique()):
    print(f"Processing group {group}...")
    group_start = time()

    filename = src_dir / f"indicators_{group}.tif"
    outfilename = out_dir / f"sa_indicators_{group}.mbtiles"

    rows = df.loc[df.group == group]

    encoding = rows[["id", "offset", "bits", "value_shift"]].to_dict(orient="records")

    tif_to_mbtiles(
        filename,
        outfilename,
        min_zoom=min_zoom,
        max_zoom=max_zoom,
        tile_size=tile_size,
        tile_renderer=renderer,
        metadata={
            "name": "South Atlantic Conservation Blueprint 2021 Indicators",
            "description": "Indicators used in the South Atlantic Conservation Blueprint 2021",
            "attribution": "South Atlantic Conservation Blueprint 2021",
            "encoding": json.dumps(encoding),
        },
    )
    print("Group done in {:.2f} min".format((time() - group_start) / 60.0))


print("All done in {:.2f}".format((time() - start) / 60))
