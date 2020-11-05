"""
Calculate statistics for each HUC12 and marine lease block using
the Blueprint, indicators, SLR, Urbanization, and ownership datasets.
"""

import csv
import os
from pathlib import Path
from time import time

import pandas as pd
import geopandas as gp

from analysis.lib.stats import (
    summarize_bluprint_by_huc12,
    summarize_bluprint_by_marine_block,
    summarize_urban_by_huc12,
    summarize_slr_by_huc12,
    summarize_ownership_by_huc12,
    summarize_counties_by_huc12,
    summarize_parca_by_huc12,
)

data_dir = Path("data")
huc12_filename = data_dir / "inputs/summary_units/huc12.feather"
marine_filename = data_dir / "inputs/summary_units/marine_blocks.feather"


#########################################################################
########### Subwatersheds (HUC12) #######################################
#########################################################################
start = time()

out_dir = data_dir / "results/huc12"
if not out_dir.exists():
    os.makedirs(out_dir)

print("Reading HUC12 boundaries")
units_df = gp.read_feather(huc12_filename, columns=["id", "geometry"]).set_index("id")

# transform to pandas Series instead of GeoSeries to get pygeos geometries for iterators below
geometries = pd.Series(units_df.geometry.values.data, index=units_df.index)

# Summarize Blueprint, corridors, and indicators
summarize_bluprint_by_huc12(geometries)

# Summarize current and projected urbanization
summarize_urban_by_huc12(geometries)

# Summarize projected sea level rise
summarize_slr_by_huc12(geometries)

# Calculate overlap with ownership and protection
summarize_ownership_by_huc12(units_df)

# Calculate overlap with counties
summarize_counties_by_huc12(units_df)

summarize_parca_by_huc12(units_df)

print(
    "Processed {:,} zones in {:.2f}m".format(len(geometries), (time() - start) / 60.0)
)


# #########################################################################
# ########### Marine Lease Blocks #########################################
# #########################################################################
# start = time()

# out_dir = data_dir / "results/marine_blocks"
# if not out_dir.exists():
#     os.makedirs(out_dir)

# print("Reading marine blocks boundaries")
# units_df = gp.read_feather(marine_filename, columns=["id", "geometry"]).set_index("id")

# geometries = pd.Series(units_df.geometry.values.data, index=units_df.index)

# # Summarize Blueprint and input areas
# summarize_bluprint_by_marine_block(geometries)

# print(
#     "Processed {:,} zones in {:.2f}m".format(len(geometries), (time() - start) / 60.0)
# )
