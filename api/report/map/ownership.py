from io import BytesIO
from copy import deepcopy
import logging

import httpx
from PIL import Image

from api.settings import MBGL_SERVER_URL
from constants import OWNERSHIP

log = logging.getLogger(__name__)


# interleave keys and colors for mapbox
color_expr = (
    ["match", ["get", "FEE_ORGTYP"]]
    + [v for k, e in OWNERSHIP.items() for v in (k, e["color"])]
    + ["#FFF"]
)


STYLE = {
    "version": 8,
    "sources": {
        "ownership": {"type": "vector", "url": "mbtiles://ownership", "tileSize": 256}
    },
    "layers": [
        {
            "id": "fill",
            "source": "ownership",
            "source-layer": "ownership",
            "type": "fill",
            "paint": {"fill-opacity": 0.7, "fill-color": color_expr},
        },
        {
            "id": "outline",
            "source": "ownership",
            "source-layer": "ownership",
            "type": "line",
            "paint": {"line-width": 0.5, "line-color": "#AAAAAA", "line-opacity": 1},
        },
    ],
}


async def get_ownership_map_image(center, zoom, width, height):
    """Create a rendered map image of land owner values from ownership data.

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

    params = {
        "style": STYLE,
        "center": center,
        "zoom": zoom,
        "width": width,
        "height": height,
    }

    try:
        async with httpx.AsyncClient() as client:
            r = await client.post(MBGL_SERVER_URL, json=params)

        if r.status_code != 200:
            log.error(f"Error generating ownership image: {r.text[:255]}")
            return None

        return Image.open(BytesIO(r.content))

    except Exception as ex:
        log.error(f"Error generating ownership image: {ex}")
        return None
