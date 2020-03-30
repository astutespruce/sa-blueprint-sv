from base64 import b64encode
from datetime import date
from io import BytesIO
from pathlib import Path

from weasyprint import HTML
from jinja2 import Environment, PackageLoader

from constants import BLUEPRINT, ECOSYSTEMS, INDICATORS_INDEX
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


def create_report(maps, results):
    template = env.get_template("report.html")

    title = "South Atlantic Conservation Blueprint Summary"
    subtitle = ""
    if "name" in results:
        subtitle = f"for {results['name']}"
        if "type" in results:
            subtitle += " " + results["type"]

    context = {
        "date": date.today().strftime("%m/%d/%y"),
        "title": title,
        "subtitle": subtitle,
        "url": "https://blueprint.southatlanticlcc.org/",
        "maps": maps,
        "blueprint": BLUEPRINT,
        "ecosystems": ECOSYSTEMS,
        "indicators": INDICATORS_INDEX,
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
