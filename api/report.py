from base64 import b64encode
from copy import deepcopy
from datetime import date
from io import BytesIO
from operator import itemgetter
from pathlib import Path

from weasyprint import HTML
from jinja2 import Environment, PackageLoader

from constants import (
    BLUEPRINT,
    ECOSYSTEMS,
    INDICATORS_INDEX,
    PLANS,
    URBAN_LEGEND,
    SLR_LEGEND,
)
from util.format import format_number as format_number


def reverse_filter(iterable):
    return list(iterable)[::-1]


assets_dir = Path(__file__).parent / "templates/assets"


def load_asset(path):
    # data:image/svg+xml;
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


env = Environment(loader=PackageLoader("api", "templates"))
env.filters["reverse"] = reverse_filter
env.filters["format_number"] = format_number
env.filters["load_asset"] = load_asset
env.filters["sum"] = sum


def create_report(maps, results):
    template = env.get_template("report.html")

    title = "South Atlantic Conservation Blueprint Summary"
    subtitle = ""
    if "name" in results:
        subtitle = f"for {results['name']}"
        if "type" in results:
            subtitle += " " + results["type"]

    # Extract ecosystems with results
    ecosystems = []
    for ecosystem in ECOSYSTEMS:
        ecosystem = deepcopy(ecosystem)

        if ecosystem.get("extent", None) == "region":
            if results["type"] == "subwatershed":
                ecosystem["acres"] = 0  # just to force sort at end
                ecosystems.append(ecosystem)

            continue

        ecosystem["acres"] = results["ecosystems"][ecosystem["value"]]
        if ecosystem["acres"]:
            ecosystems.append(ecosystem)

    # sort on acres, inner sort alphabetic on label
    ecosystems = sorted(
        sorted(ecosystems, key=itemgetter("label")),
        key=itemgetter("acres"),
        reverse=True,
    )

    ecosystem_acres = sum([e["acres"] for e in ecosystems])

    ownership_acres = sum([e["acres"] for e in results.get("ownership", [])])
    protection_acres = sum([e["acres"] for e in results.get("protection", [])])

    legends = {
        # sort descending, omit not a priority
        "blueprint": BLUEPRINT[:0:-1]
    }
    for indicator_id in results["indicators"]:
        indicator = INDICATORS_INDEX[indicator_id]
        colors = indicator["colors"]
        legend = []
        for value, label in indicator["values"].items():
            if value in colors:
                legend.append({"value": value, "label": label, "color": colors[value]})

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

    context = {
        "date": date.today().strftime("%m/%d/%y"),
        "title": title,
        "subtitle": subtitle,
        "url": "https://blueprint.southatlanticlcc.org/",
        "maps": maps,
        "legends": legends,
        "blueprint": BLUEPRINT,
        "ecosystems": ecosystems,
        "ecosystem_acres": ecosystem_acres,
        "ownership_acres": ownership_acres,
        "protection_acres": protection_acres,
        "indicators": INDICATORS_INDEX,
        "plans": PLANS,
        "results": results,
    }

    # Render variables as needed into the CSS
    css = env.get_template("report.css").render(**context)
    context["css"] = css

    print("Creating report...")

    with open("/tmp/test.html", "w") as out:
        out.write(template.render(**context))

    return HTML(
        BytesIO((template.render(**context)).encode())
        # , url_fetcher=url_fetcher
    ).write_pdf()
