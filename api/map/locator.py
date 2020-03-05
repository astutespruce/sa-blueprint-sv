from copy import deepcopy
from io import BytesIO

import httpx
from PIL import Image


from settings import MBGL_SERVER_URL

ZOOM = 3
# TODO: derive from SA_bounds poly
CENTER = [-81, 31.734804]
WIDTH = 200
HEIGHT = 200


LOCATOR_STYLE = {
    "version": 8,
    "sources": {
        "basemap": {
            "type": "raster",
            "url": "mbtiles://basemap_esri_ocean",
            "tileSize": 256,
        },
        "states": {"type": "vector", "url": "mbtiles://states", "tileSize": 256},
        "marker": {"type": "geojson", "data": ""},
    },
    "layers": [
        {"id": "basemap", "type": "raster", "source": "basemap"},
        {
            "id": "states",
            "source": "states",
            "source-layer": "states",
            "type": "line",
            "paint": {"line-color": "#444444", "line-width": 1, "line-opacity": 1},
        },
        {
            "id": "marker",
            "source": "marker",
            "type": "circle",
            "paint": {
                "circle-color": "#FF0000",
                "circle-radius": 4,
                "circle-opacity": 1,
            },
        },
    ],
}


def get_locator_map_image(longitude, latitude):
    """
    Create a rendered locator map image.

    Parameters
    ----------
    latitude : float
        latitude of area of interest marker
    longitude : float
        longitude of area of interest marker

    Returns
    -------
    Image object
    """

    style = deepcopy(LOCATOR_STYLE)
    style["sources"]["marker"]["data"] = {
        "type": "Point",
        "coordinates": [longitude, latitude],
    }

    params = {
        "style": style,
        "center": CENTER,
        "zoom": ZOOM,
        "width": WIDTH,
        "height": HEIGHT,
    }

    try:
        r = httpx.post(MBGL_SERVER_URL, json=params)
        r.raise_for_status()
        return Image.open(BytesIO(r.content))

    except Exception:
        return None

