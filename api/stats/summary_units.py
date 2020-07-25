from collections import defaultdict
from pathlib import Path

from geofeather.pygeos import from_geofeather
import numpy as np
import pandas as pd
import pygeos as pg


from analysis.constants import (
    BLUEPRINT,
    INDICATORS,
    INDICATOR_INDEX,
    OWNERSHIP,
    PROTECTION,
)


class SummaryUnits(object):
    def __init__(self, unit_type="huc12"):
        print(f"Loading {unit_type} summary data...")
        self.unit_type = unit_type

        working_dir = Path("data/derived") / unit_type

        id_field = "HUC12" if unit_type == "huc12" else "id"

        self.units = from_geofeather(
            working_dir / f"{unit_type}_wgs84.feather"
        ).set_index(id_field)

        self.blueprint = pd.read_feather(working_dir / "blueprint.feather").set_index(
            id_field
        )

        if unit_type == "huc12":
            self.slr = pd.read_feather(working_dir / "slr.feather").set_index(id_field)
            self.urban = pd.read_feather(working_dir / "urban.feather").set_index(
                id_field
            )
            self.ownership = pd.read_feather(
                working_dir / "ownership.feather"
            ).set_index(id_field)

            self.protection = pd.read_feather(
                working_dir / "protection.feather"
            ).set_index(id_field)

            self.counties = pd.read_feather(working_dir / "counties.feather").set_index(
                id_field
            )

    def get_results(self, id):
        if not id in self.units.index:
            raise ValueError("ID not in units index")

        unit = self.units.loc[id]
        results = unit[unit.index.difference(["geometry"])].to_dict()
        results["bounds"] = pg.bounds(unit.geometry).tolist()
        results["type"] = (
            "subwatershed" if self.unit_type == "huc12" else "marine lease block"
        )
        results["is_marine"] = self.unit_type == "marine_blocks"

        blueprint = None
        try:
            blueprint = self.blueprint.loc[id]

        except KeyError:
            # no Blueprint results, there won't be other results
            return results

        # unpack blueprint, corridors, and indicators
        results["blueprint_total"] = blueprint["shape_mask"]
        results["blueprint"] = [
            getattr(blueprint, c) for c in blueprint.index if c.startswith("blueprint_")
        ]

        results["corridors"] = [
            getattr(blueprint, c) for c in blueprint.index if c.startswith("corridors_")
        ]
        results["corridors_total"] = sum(results["corridors"])

        groups = {c.rsplit("_", 1)[0] for c in blueprint.index}

        indicators = []
        for indicator_id, indicator in INDICATOR_INDEX.items():
            if indicator_id not in groups:
                continue

            values = [
                getattr(blueprint, c)
                for c in blueprint.index
                if c.startswith(indicator_id)
            ]
            # drop indicators that are not present
            if max(values):
                indicators.append(indicator_id)
                results[indicator_id] = values
                results[f"{indicator_id}_total"] = sum(values)

                if "goodThreshold" in indicator:
                    results[f"{indicator_id}_good_total"] = sum(
                        values[indicator["goodThreshold"] :]
                    )

        results["indicators"] = indicators

        if self.unit_type != "huc12":
            return results

        try:
            ownership = self.ownership.loc[self.ownership.index.isin([id])]
            ownerships_present = ownership.FEE_ORGTYP.unique()
            # use the native order of OWNERSHIP to drive order of results
            ownership_results = [
                {
                    "label": value["label"],
                    "acres": ownership.loc[ownership.FEE_ORGTYP == key].iloc[0].acres,
                }
                for key, value in OWNERSHIP.items()
                if key in ownerships_present
            ]
            results["ownership"] = ownership_results

        except KeyError:
            pass

        try:
            protection = self.protection.loc[self.protection.index.isin([id])]
            protection_present = protection.GAP_STATUS.unique()
            # use the native order of PROTECTION to drive order of results
            protection_results = [
                {
                    "label": value["label"],
                    "acres": protection.loc[protection.GAP_STATUS == key].iloc[0].acres,
                }
                for key, value in PROTECTION.items()
                if key in protection_present
            ]

            results["protection"] = protection_results

        except KeyError:
            pass

        try:
            counties = self.counties.loc[self.counties.index.isin([id])].sort_values(
                by=["state", "county"]
            )
            results["counties"] = counties.to_dict(orient="records")

        except KeyError:
            pass

        try:
            slr = self.slr.loc[id]
            if slr[1:].max():
                results["slr_acres"] = slr.shape_mask
                results["slr"] = slr[1:].tolist()

        except KeyError:
            pass

        try:
            urban = self.urban.loc[id]
            if urban[1:].max():
                results["urban_acres"] = urban.shape_mask
                results["urban"] = urban[1]
                results["proj_urban"] = urban[2:].tolist()

        except KeyError:
            pass

        return results
