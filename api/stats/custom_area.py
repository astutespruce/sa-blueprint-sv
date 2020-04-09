import csv
import os
from pathlib import Path
from time import time
import warnings

import pandas as pd
from geofeather.pygeos import from_geofeather, to_geofeather
import numpy as np
from progress.bar import Bar
import pygeos as pg
import rasterio
from rasterio.mask import raster_geometry_mask

from util.io import write_raster
from util.pygeos_util import to_crs, to_dict, sjoin, sjoin_geometry, intersection
from constants import (
    BLUEPRINT,
    INDICATORS_INDEX,
    URBAN_YEARS,
    DATA_CRS,
    GEO_CRS,
    OWNERSHIP,
    PROTECTION,
    M2_ACRES,
)
from stats import (
    extract_count_in_geometry,
    extract_blueprint_indicator_area,
    extract_urbanization_area,
    extract_slr_area,
)


data_dir = Path("data")
ownership_filename = data_dir / "boundaries/ownership.feather"
county_filename = data_dir / "boundaries/counties.feather"
slr_bounds_filename = data_dir / "threats/slr/slr_bounds.feather"


class CustomArea(object):
    def __init__(self, geometry, crs, name):
        self.geometry = to_crs(geometry, crs, DATA_CRS)
        # wrap geometry as a dict for rasterio
        self.shapes = np.asarray([to_dict(self.geometry[0])])
        self.name = name

    def get_blueprint(self):
        blueprint = extract_blueprint_indicator_area(self.shapes)

        if blueprint is None:
            return None

        results = {
            "blueprint_acres": blueprint["shape_mask"],
            "blueprint": blueprint["blueprint"],
            "ecosystems": blueprint["ecosystems"],
        }

        indicators = []
        for indicator in INDICATORS_INDEX.keys():
            # drop indicators that are not present
            if blueprint[indicator].max() > 0:
                results[indicator] = blueprint[indicator]
                indicators.append(indicator)

        results["indicators"] = indicators

        return results

    def get_urban(self):
        urban_results = extract_urbanization_area(self.shapes)

        if urban_results is None:
            return None

        return {
            "urban_acres": urban_results["shape_mask"],
            "urban": urban_results["urban"],
            "proj_urban": [urban_results[year] for year in URBAN_YEARS],
        }

    def get_slr(self):
        slr_bounds = from_geofeather(slr_bounds_filename).geometry
        idx = sjoin_geometry(self.geometry, slr_bounds.values, how="inner")
        if not len(idx):
            return None

        slr_results = extract_slr_area(self.shapes.take(idx.index.unique()))

        return {
            "slr_acres": slr_results["shape_mask"],
            "slr": [slr_results[i] for i in range(7)],
        }

    def get_counties(self):
        counties = from_geofeather(
            county_filename, columns=["geometry", "FIPS", "state", "county"]
        )
        df = (
            sjoin(pd.DataFrame({"geometry": self.geometry}), counties)[
                ["FIPS", "state", "county"]
            ]
            .reset_index(drop=True)
            .sort_values(by=["state", "county"])
        )

        if not len(df):
            return None

        return {"counties": df.to_dict(orient="records")}

    def get_ownership(self):
        ownership = from_geofeather(
            ownership_filename, columns=["geometry", "FEE_ORGTYP", "GAP_STATUS"]
        )

        df = intersection(pd.DataFrame({"geometry": self.geometry}), ownership)

        if not len(df):
            return None

        df["acres"] = pg.area(df.geometry_right) * M2_ACRES
        df = df.loc[df.acres > 0].copy()

        if not len(df):
            return None

        results = dict()

        by_owner = (
            df[["FEE_ORGTYP", "acres"]]
            .groupby(by="FEE_ORGTYP")
            .acres.sum()
            .astype("float32")
            .to_dict()
        )
        # use the native order of OWNERSHIP to drive order of results
        results["ownership"] = [
            {"label": value["label"], "acres": by_owner[key]}
            for key, value in OWNERSHIP.items()
            if key in by_owner
        ]

        by_protection = (
            df[["GAP_STATUS", "acres"]]
            .groupby(by="GAP_STATUS")
            .acres.sum()
            .astype("float32")
            .to_dict()
        )
        # use the native order of PROTECTION to drive order of results
        results["protection"] = [
            {"label": value["label"], "acres": by_protection[key]}
            for key, value in PROTECTION.items()
            if key in by_protection
        ]

        return results

    def get_results(self):
        results = {"type": "", "acres": pg.area(self.geometry).sum() * M2_ACRES}

        try:
            blueprint_results = self.get_blueprint()
            if blueprint_results is None:
                return None

            results.update(blueprint_results)

        except ValueError:
            # geometry does not overlap Blueprint.  There are no valid results here,
            # move along.
            return None

        urban_results = self.get_urban()
        if urban_results is not None:
            results.update(urban_results)

        slr_results = self.get_slr()
        if slr_results is not None:
            results.update(slr_results)

        ownership_results = self.get_ownership()
        if ownership_results is not None:
            results.update(ownership_results)

        county_results = self.get_counties()
        if county_results is not None:
            results.update(county_results)

        return results