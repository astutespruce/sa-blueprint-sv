from io import BytesIO
from copy import deepcopy
import logging

import httpx
import pygeos as pg
from PIL import Image

from settings import MBGL_SERVER_URL
from util.pygeos_util import to_dict


log = logging.getLogger(__name__)

STYLE = {
    "version": 8,
    "sources": {
        "aoi": {"type": "geojson", "data": ""},
        "aoi-mask": {"type": "geojson", "data": ""},
    },
    "layers": [
        {
            "id": "aoi-mask",
            "source": "aoi-mask",
            "type": "fill",
            "paint": {"fill-color": "#FFFFFF", "fill-opacity": 0.5},
        },
        {
            "id": "aoi",
            "source": "aoi",
            "type": "line",
            "paint": {"line-width": 2, "line-color": "#000000", "line-opacity": 1},
        },
    ],
}


def get_aoi_map_image(geometry, center, zoom, width, height):
    """Create a rendered map image of the area of interest.

    Parameters
    ----------
    geometry : pygeos Geometry object (singular)
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

    mask = pg.difference(pg.box(-180, -85, 180, 85), geometry)

    style = deepcopy(STYLE)
    style["sources"]["aoi-mask"]["data"] = to_dict(mask)
    style["sources"]["aoi"]["data"] = to_dict(geometry)

    params = {
        "style": style,
        "center": center,
        "zoom": zoom,
        "width": width,
        "height": height,
    }

    try:
        r = httpx.post(MBGL_SERVER_URL, json=params)
        if r.status_code != 200:
            log.error(f"Error generating AOI image: {r.text[:255]}")
            return None

        return Image.open(BytesIO(r.content))

    except Exception as ex:
        log.error(f"Error generating AOI image: {ex}")
        return None
