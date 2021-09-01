"""
Create coarser resolution overviews in raster files.
"""


from pathlib import Path

import rasterio
from rasterio.enums import Resampling

from analysis.constants import INDICATORS, OVERVIEW_FACTORS


src_dir = Path("data/inputs")
indicators_dir = src_dir / "indicators"
blueprint_filename = src_dir / "blueprint2021.tif"
corridors_filename = src_dir / "corridors.tif"
urban_dir = src_dir / "threats/urban"
slr_dir = src_dir / "threats/slr"


for filename in [blueprint_filename, corridors_filename]:
    print(f"Processing {filename.name}...")
    with rasterio.open(filename, "r+") as src:
        src.build_overviews(OVERVIEW_FACTORS, Resampling.nearest)


for indicator in INDICATORS:
    print(f"Processing {indicator['id']}...")

    with rasterio.open(indicators_dir / indicator["filename"], "r+") as src:
        src.build_overviews(OVERVIEW_FACTORS, Resampling.nearest)
