from io import BytesIO
from copy import deepcopy

import httpx
from PIL import Image

from settings import MBGL_SERVER_URL

STYLE = {
    "version": 8,
    "sources": {
        "sa_units": {"type": "vector", "url": "mbtiles://sa_units", "tileSize": 256}
    },
    "layers": [
        # there are unsightly gaps between marine units and HUC12s that don't work with this approach
        # {
        #     "id": "units-fill",
        #     "source": "units",
        #     "source-layer": "units",
        #     "type": "fill",
        #     "paint": {"fill-color": "#333333", "fill-opacity": 0.5},
        # },
        {
            "id": "mask",
            "source": "sa_units",
            "source-layer": "mask",
            "type": "fill",
            "paint": {"fill-color": "#333333", "fill-opacity": 0.5},
        },
        {
            "id": "units-outline",
            "source": "sa_units",
            "source-layer": "units",
            "type": "line",
            "paint": {"line-width": 2, "line-color": "#000000", "line-opacity": 1},
        },
    ],
}


def get_summary_unit_map_image(id, center, zoom, width, height):
    """Create a rendered map image of an existing summary unit.

    Parameters
    ----------
    id : str
        ID of summary unit
    center : [longitude, latitude]
    zoom : float
    width : int
        map width
    height : int
        map height

    Returns
    -------
    Image object
    """

    style = deepcopy(STYLE)
    # filter OUT current unit
    # style["layers"][0]["filter"] = ["!=", ["get", "id"], id]
    # filter IN current unit
    # style["layers"][1]["filter"] = ["==", ["get", "id"], id]

    style["layers"][0]["filter"] = ["==", ["get", "id"], id]

    params = {
        "style": style,
        "center": center,
        "zoom": zoom,
        "width": width,
        "height": height,
    }

    r = httpx.post(MBGL_SERVER_URL, json=params)
    return Image.open(BytesIO(r.content))
