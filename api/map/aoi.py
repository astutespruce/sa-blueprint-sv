from io import BytesIO
from copy import deepcopy

import httpx
from PIL import Image

from settings import MBGL_SERVER_URL

STYLE = {
    "version": 8,
    "sources": {
        "aoi": {"type": "geojson", "data": ""},
        "sa_units": {"type": "vector", "url": "mbtiles://sa_units", "tileSize": 256},
    },
    "layers": [
        {
            "id": "mask",
            "source": "sa_units",
            "source-layer": "mask",
            "type": "fill",
            "paint": {"fill-color": "#333333", "fill-opacity": 0.5},
        },
        {
            "id": "aoi",
            "source": "aoi",
            "type": "line",
            "paint": {"line-width": 2, "line-color": "#000000", "line-opacity": 1},
        },
    ],
}


def get_aoi_map_image(geojson, center, zoom, width, height):
    """Create a rendered map image of the area of interest.

    Parameters
    ----------
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
    style["sources"]["aoi"]["data"] = geojson

    params = {
        "style": style,
        "center": center,
        "zoom": zoom,
        "width": width,
        "height": height,
    }

    r = httpx.post(MBGL_SERVER_URL, json=params)
    return Image.open(BytesIO(r.content))
