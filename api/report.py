from datetime import date
from io import BytesIO

from weasyprint import HTML
from jinja2 import Environment, PackageLoader

from constants import BLUEPRINT, ECOSYSTEMS, INDICATORS_INDEX


def reverse_filter(iterable):
    return list(iterable)[::-1]


env = Environment(loader=PackageLoader("api", "templates"))
env.filters["reverse"] = reverse_filter


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
        "url": "TODO: URL",
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

    return HTML(BytesIO((template.render(**context)).encode())).write_pdf()
