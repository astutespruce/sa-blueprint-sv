from datetime import date
from io import BytesIO

from weasyprint import HTML
from jinja2 import Environment, PackageLoader

from constants import BLUEPRINT

env = Environment(loader=PackageLoader("api", "templates"))


def create_report(maps, blueprint_results, aoi_name=None, aoi_type_label=None):
    template = env.get_template("report.html")

    title = "South Atlantic Conservation Blueprint Summary"

    context = {
        "date": date.today().strftime("%m/%d/%y"),
        "title": title,
        "url": "TODO: URL",
        "aoi_name": aoi_name,
        "aoi_type_label": aoi_type_label,
        "maps": maps,
        # omit Not a priority
        "blueprint_legend": BLUEPRINT[:0:-1],
        "blueprint_results": blueprint_results,
    }

    # Render variables as needed into the CSS
    css = env.get_template("report.css").render(**context)
    context["css"] = css

    print("Creating report...")

    with open("/tmp/test.html", "w") as out:
        out.write(template.render(**context))

    return HTML(BytesIO((template.render(**context)).encode())).write_pdf()
