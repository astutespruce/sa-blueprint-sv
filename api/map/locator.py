from copy import deepcopy
from io import BytesIO
import os

from dotenv import load_dotenv
import httpx
from PIL import Image


load_dotenv()
ACCESS_TOKEN = os.getenv("MAPBOX_ACCESS_TOKEN")
MBGL_SERVER_URL = os.getenv("MBGL_SERVER_URL", "http://localhost:8001/render")


# TODO: derive from SA_bounds poly
# BOUNDS = [-91.538086, 24.647017, -72.202148, 38.822591]
ZOOM = 3
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


def get_locator_map(longitude, latitude):
    """
    Create a rendered locator map image.

    Parameters
    ----------
    latitude : float
        latitude of centerpoint
    longitude : float
        longitude of centerpoint
    width: int
        width of the image in pixels
    height: int
        height of the image in pixels

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

