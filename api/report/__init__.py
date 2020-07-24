from base64 import b64encode
from collections import OrderedDict
from copy import deepcopy
from datetime import date
from io import BytesIO
from operator import itemgetter
from pathlib import Path

from weasyprint import HTML
from jinja2 import Environment, FileSystemLoader

from analysis.constants import (
    BLUEPRINT,
    ECOSYSTEM_INDEX,
    ECOSYSTEM_GROUPS,
    INDICATOR_INDEX,
    CORRIDORS,
    URBAN_LEGEND,
    SLR_LEGEND,
    OWNERSHIP,
    PROTECTION,
    DEBUG,
)
from api.report.format import format_number


def reverse_filter(iterable):
    return list(iterable)[::-1]


assets_dir = Path(__file__).parent / "templates/assets"


def load_asset(path):
    prefix = ""
    data = ""

    if path.endswith(".png"):
        prefix = "data:image/png;base64,"

    elif path.endswith(".svg"):
        prefix = "data:image/svg+xml;base64,"

    else:
        raise NotImplementedError(f"{path} not a handled type")

    data = b64encode(open(assets_dir / path, "rb").read()).decode("utf-8")
    return f"{prefix}{data}"


template_path = Path(__file__).parent.resolve() / "templates"

env = Environment(loader=FileSystemLoader(template_path))
env.filters["reverse"] = reverse_filter
env.filters["format_number"] = format_number
env.filters["load_asset"] = load_asset
env.filters["sum"] = sum

template = env.get_template("report.html")
css_template = env.get_template("report.css")


def create_report(maps, results):
    title = "South Atlantic Conservation Blueprint Summary"
    subtitle = ""
    if "name" in results:
        subtitle = f"for {results['name']}"
        if "type" in results:
            subtitle += " " + results["type"]

    # determine ecosystems present from indicators
    ecosystem_ids = {id.split("_")[0] for id in results["indicators"]}
    # ecosystems = {id: ECOSYSTEM_INDEX[id] for id in ecosystem_ids}

    # determine ecosystem groups present from ecosystems
    # ecosystem_groups = OrderedDict()
    ecosystem_groups = []
    for group in ECOSYSTEM_GROUPS:
        ecosystems_present = set(group["ecosystems"]).intersection(ecosystem_ids)
        if not ecosystems_present:
            continue

        ecosystems = []
        for id in ecosystems_present:
            # update ecosystem with only indicators that are present
            ecosystem = deepcopy(ECOSYSTEM_INDEX[id])
            ecosystem["indicators"] = [
                INDICATOR_INDEX[i]
                for i in sorted(
                    {f"{id}_{i}" for i in ecosystem["indicators"]}.intersection(
                        results["indicators"]
                    )
                )
            ]
            ecosystems.append(ecosystem)

        ecosystem_groups.append(
            {
                "id": group["id"],
                "label": group["label"],
                "color": group["color"],
                "borderColor": group["borderColor"],
                "ecosystems": ecosystems,
            }
        )

    ownership_acres = sum([e["acres"] for e in results.get("ownership", [])])
    protection_acres = sum([e["acres"] for e in results.get("protection", [])])

    legends = {
        # sort Blueprint descending order
        "blueprint": BLUEPRINT[::-1],
        "corridors": CORRIDORS,
    }
    for indicator_id in results["indicators"]:
        indicator = INDICATOR_INDEX[indicator_id]
        legend = indicator["values"].copy()
        legend.reverse()
        legends[indicator_id] = legend

    if "urban" in results:
        legends["urban"] = (
            URBAN_LEGEND[1:3]
            + URBAN_LEGEND[5:6]
            + URBAN_LEGEND[8:9]
            + URBAN_LEGEND[11:12]
            + URBAN_LEGEND[-1:]
        )

    if "slr" in results:
        legends["slr"] = SLR_LEGEND

    if "ownership" in results:
        legends["ownership"] = list(OWNERSHIP.values())

    if "protection" in results:
        legends["protection"] = list(PROTECTION.values())

    context = {
        "date": date.today().strftime("%m/%d/%y"),
        "title": title,
        "subtitle": subtitle,
        "url": "https://blueprint.southatlanticlcc.org/",
        "maps": maps,
        "legends": legends,
        # "ecosystems": ecosystems,
        "ecosystem_groups": ecosystem_groups,
        "ownership_acres": ownership_acres,
        "protection_acres": protection_acres,
        "indicators": INDICATOR_INDEX,
        "results": results,
    }

    # Render variables as needed into the CSS
    css = css_template.render(**context)
    context["css"] = css

    print("Creating report...")

    # FIXME:
    if DEBUG:
        with open("/tmp/test.html", "w") as out:
            out.write(template.render(**context))

    return HTML(BytesIO((template.render(**context)).encode())).write_pdf()
