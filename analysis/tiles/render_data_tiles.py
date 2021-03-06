from time import time
from pathlib import Path
import json

import pandas as pd
from tilecutter.mbtiles import tif_to_mbtiles


src_dir = Path("data/for_tiles")
out_dir = Path("tiles")


tile_size = 128
min_zoom = 7
max_zoom = 14  # NOTE: z14 takes 2+ hours per tileset


df = pd.read_feather(src_dir / "encoding.feather")

start = time()

for group in sorted(df.group.unique()):
    print(f"Processing group {group}...")
    group_start = time()

    filename = src_dir / f"indicators_{group}.tif"
    outfilename = out_dir / f"sa_indicators_{group}.mbtiles"

    rows = df.loc[df.group == group]

    encoding = {
        "bits": rows.bits.sum().item() + len(rows),
        "layers": rows[["id", "bits"]].to_dict(orient="records"),
    }

    tif_to_mbtiles(
        filename,
        outfilename,
        min_zoom=min_zoom,
        max_zoom=max_zoom,
        tile_size=tile_size,
        metadata={
            "name": "South Atlantic Conservation Blueprint 2020 Indicators",
            "description": "Indicators used in the South Atlantic Conservation Blueprint 2020",
            "attribution": "South Atlantic Conservation Blueprint 2020",
            "encoding": json.dumps(encoding),
        },
    )
    print("Group done in {:.2f} min".format((time() - group_start) / 60.0))


print("All done in {:.2f}".format((time() - start) / 60))
