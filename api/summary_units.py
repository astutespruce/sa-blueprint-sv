from pathlib import Path

from geofeather.pygeos import from_geofeather
import pandas as pd
import pygeos as pg

from constants import BLUEPRINT, INDICATORS, INDICATORS_INDEX


class SummaryUnits(object):
    def __init__(self, unit_type="huc12"):
        print(f"Loading {unit_type} summary data...")
        self.unit_type = unit_type

        working_dir = Path("data/derived") / unit_type

        id_field = "HUC12" if unit_type == "huc12" else "id"

        self.units = from_geofeather(working_dir / f"{unit_type}.feather").set_index(
            id_field
        )

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

        else:
            # TODO: set marine ecosystem to 100%
            raise NotImplementedError("Not done yet!")

    def get_results(self, id):
        if not id in self.units.index:
            raise ValueError("ID not in units index")

        unit = self.units.loc[id]
        results = unit[unit.index.difference(["geometry"])].to_dict()
        results["bounds"] = pg.bounds(unit.geometry)
        results["type"] = (
            "subwatershed" if self.unit_type == "huc12" else "marine lease block"
        )

        blueprint = None
        try:
            blueprint = self.blueprint.loc[id]
        except KeyError:
            # no Blueprint results, there won't be other results
            return results

        # unpack blueprint, ecosystems, indicators
        results["blueprint_acres"] = blueprint["shape_mask"]
        results["blueprint"] = [
            getattr(blueprint, c) for c in blueprint.index if c.startswith("blueprint_")
        ]

        groups = {c.rsplit("_", 1)[0] for c in blueprint.index}

        # TODO: handle marine
        if "ecosystems" in groups:
            results["ecosystems"] = [
                getattr(blueprint, c)
                for c in blueprint.index
                if c.startswith("ecosystems_")
            ]

        indicators = []
        for indicator in INDICATORS_INDEX.keys():
            if indicator not in groups:
                continue

            values = [
                getattr(blueprint, c)
                for c in blueprint.index
                if c.startswith(indicator)
            ]
            # drop indicators that are not present
            if max(values):
                results[indicator] = values
                indicators.append(indicator)

        results["indicators"] = indicators

        return results
