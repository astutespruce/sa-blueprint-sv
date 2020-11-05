from pathlib import Path

import geopandas as gp
import pygeos as pg

from analysis.constants import M2_ACRES
from analysis.lib.pygeos_util import intersection


ownership_filename = "data/inputs/boundaries/ownership.feather"

results_dir = Path("data/results/huc12")
ownership_results_filename = results_dir / "ownership.feather"
protection_results_filename = results_dir / "protection.feather"


def summarize_by_huc12(units_df):
    print("Calculating overlap with land ownership and protection")

    ownership = gp.read_feather(
        ownership_filename, columns=["geometry", "FEE_ORGTYP", "GAP_STATUS"]
    )

    index_name = units_df.index.name

    df = intersection(units_df, ownership)

    if not len(df):
        return

    df["acres"] = pg.area(df.geometry_right.values.data) * M2_ACRES

    # drop areas that touch but have no overlap
    df = df.loc[df.acres > 0].copy()

    by_owner = (
        df[["FEE_ORGTYP", "acres"]]
        .groupby([index_name, "FEE_ORGTYP"])
        .acres.sum()
        .astype("float32")
        .round()
        .reset_index()
    )

    by_protection = (
        df[["GAP_STATUS", "acres"]]
        .groupby([index_name, "GAP_STATUS"])
        .acres.sum()
        .astype("float32")
        .round()
        .reset_index()
    )

    by_owner.to_feather(ownership_results_filename)
    by_protection.to_feather(protection_results_filename)

