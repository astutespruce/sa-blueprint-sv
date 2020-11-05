import geopandas as gp

import pygeos as pg
from analysis.constants import M2_ACRES
from analysis.lib.pygeos_util import intersection


parca_filename = "data/inputs/boundaries/parca.feather"
results_filename = "data/results/huc12/parca.feather"


def summarize_by_huc12(units_df):
    """Calculate spatial join with counties

    Parameters
    ----------
    df : GeoDataFrame
        summary units
    """

    print("Calculating overlap with PARCAs")
    parca = gp.read_feather(parca_filename)

    df = intersection(units_df, parca)
    df["acres"] = pg.area(df.geometry_right.values.data) * M2_ACRES

    # drop areas that touch but have no overlap
    df = df.loc[df.acres > 0].copy()

    # aggregate these back up by ID
    by_parca = (
        df[["parca_id", "name", "description", "acres"]]
        .groupby(by=[df.index.get_level_values(0), "parca_id"])
        .agg({"name": "first", "description": "first", "acres": "sum"})
        .reset_index()
        .rename(columns={"level_0": "id"})
    )
    by_parca.acres = by_parca.acres.astype("float32").round()

    by_parca.to_feather(results_filename)
