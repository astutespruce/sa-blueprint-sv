from pathlib import Path

import pandas as pd
import numpy as np
import pygeos as pg
import geopandas as gp

from analysis.pygeos_util import to_crs, to_dict, sjoin, sjoin_geometry, intersection
from analysis.constants import (
    BLUEPRINT,
    INDICATORS,
    INDICATOR_INDEX,
    URBAN_YEARS,
    DATA_CRS,
    GEO_CRS,
    OWNERSHIP,
    PROTECTION,
    M2_ACRES,
)
from analysis.stats import (
    extract_blueprint_indicator_area,
    extract_urbanization_area,
    extract_slr_area,
)


data_dir = Path("data/inputs")
boundary_filename = data_dir / "boundaries/sa_boundary.feather"
county_filename = data_dir / "boundaries/counties.feather"
parca_filename = data_dir / "boundaries/parca.feather"
ownership_filename = data_dir / "boundaries/ownership.feather"
slr_bounds_filename = data_dir / "threats/slr/slr_bounds.feather"

# Load targets into memory for faster calculations below
sa_bnd = gp.read_feather(boundary_filename)
counties = gp.read_feather(county_filename)[["geometry", "FIPS", "state", "county"]]
parca = gp.read_feather(parca_filename)
ownership = gp.read_feather(ownership_filename)
slr_bounds = gp.read_feather(slr_bounds_filename).geometry


class CustomArea(object):
    def __init__(self, geometry, crs, name):
        """Initialize a custom area from a pygeos geometry.

        Parameters
        ----------
        geometry : pygeos Geometry
        crs : pyproj CRS object
        name : string
            name of custom area
        """

        self.geometry = to_crs(geometry, crs, DATA_CRS)
        # wrap geometry as a dict for rasterio
        self.shapes = np.asarray([to_dict(self.geometry[0])])
        self.name = name

    def get_blueprint(self):
        blueprint = extract_blueprint_indicator_area(
            self.shapes, bounds=pg.total_bounds(self.geometry)
        )

        if blueprint is None:
            return None

        counts = blueprint["counts"]

        blueprint_total = counts["blueprint"].sum()

        remainder = abs(counts["shape_mask"] - blueprint_total)
        # there are small rounding errors
        remainder = remainder if remainder >= 1 else 0

        results = {
            "analysis_acres": counts["shape_mask"],
            "analysis_remainder": remainder,
            "blueprint": counts["blueprint"].tolist(),
            "blueprint_total": blueprint_total,
            "corridors": counts["corridors"].tolist(),
            "corridors_total": counts["corridors"].sum(),
        }

        indicators = []
        for indicator in INDICATORS:
            # drop indicators that are not present
            id = indicator["id"]
            if id not in counts:
                continue

            values = counts[id]

            # drop indicators that are not present in this area
            # if only 0 values are present, ignore this indicator
            if values[1:].max() > 0:
                indicators.append(id)
                results[id] = values

                min_value = indicator["values"][0]["value"]
                results[f"{id}_total"] = values[min_value:].sum()

                if "goodThreshold" in indicator:
                    results[f"{id}_good_total"] = values[
                        indicator["goodThreshold"] :
                    ].sum()

        results["indicators"] = indicators

        return results

    def get_urban(self):
        urban_results = extract_urbanization_area(
            self.shapes, bounds=pg.total_bounds(self.geometry)
        )

        if urban_results is None or urban_results["shape_mask"] == 0:
            return None

        # only keep through 2060
        proj_urban = [urban_results[year] for year in URBAN_YEARS[:5]]
        if not sum(proj_urban):
            return None

        return {
            "urban_acres": urban_results["shape_mask"],
            "urban": urban_results["urban"],
            "proj_urban": proj_urban,
        }

    def get_slr(self):
        idx = sjoin_geometry(self.geometry, slr_bounds.values.data, how="inner")
        if not len(idx):
            return None
        idx = idx.index.unique()

        slr_results = extract_slr_area(
            self.shapes.take(idx), bounds=pg.total_bounds(self.geometry.take(idx))
        )
        if slr_results is None or slr_results["shape_mask"] == 0:
            return None

        slr = [slr_results[i] for i in range(7)]
        if not sum(slr):
            return None

        return {"slr_acres": slr_results["shape_mask"], "slr": slr}

    def get_counties(self):
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

    def get_parca(self):
        df = intersection(pd.DataFrame({"geometry": self.geometry}), parca)

        if not len(df):
            return None

        df["acres"] = pg.area(df.geometry_right.values.data) * M2_ACRES
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

        return {
            "parca": by_parca[["name", "description", "acres"]].to_dict(
                orient="records"
            )
        }

    def get_ownership(self):
        df = intersection(pd.DataFrame({"geometry": self.geometry}), ownership)

        if not len(df):
            return None

        df["acres"] = pg.area(df.geometry_right.values.data) * M2_ACRES
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

        by_area = (
            df[["AREA_NAME", "FEE_OWNER", "acres"]]
            .groupby(by=[df.index.get_level_values(0), "AREA_NAME", "FEE_OWNER"])
            .acres.sum()
            .astype("float32")
            .round()
            .reset_index()
            .rename(
                columns={"level_0": "id", "AREA_NAME": "name", "FEE_OWNER": "owner"}
            )
            .sort_values(by="acres", ascending=False)
        )
        # drop very small areas, these are not helpful
        by_area = by_area.loc[by_area.acres >= 1].copy()

        results["protected_areas"] = by_area.head(25).to_dict(orient="records")
        results["num_protected_areas"] = len(by_area)

        return results

    def get_results(self):

        # if area of interest does not intersect SA boundary, there will be no results
        if not pg.intersects(self.geometry, sa_bnd.geometry.values.data).max():
            return None

        results = {
            "type": "",
            "acres": pg.area(self.geometry).sum() * M2_ACRES,
            "name": self.name,
        }

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

        parca_results = self.get_parca()
        if parca_results is not None:
            results.update(parca_results)

        return results
