from copy import deepcopy
from io import BytesIO
import logging

import httpx
from PIL import Image

from api.settings import MBGL_SERVER_URL


log = logging.getLogger(__name__)

ZOOM = 2.8
CENTER = [-78.593, 33.221]
WIDTH = 150
HEIGHT = 150


# basemap from: "https://services.arcgisonline.com/arcgis/rest/services/Ocean/World_Ocean_Base/MapServer/tile/{z}/{y}/{x}"

LOCATOR_STYLE = {
    "version": 8,
    "sources": {
        "basemap": {
            "type": "raster",
            "url": "mbtiles://basemap_esri_ocean",
            "tileSize": 256,
        },
        "states": {"type": "vector", "url": "mbtiles://states"},
        "map_units": {"type": "vector", "url": "mbtiles://map_units"},
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
            "id": "mask",
            "source": "map_units",
            "source-layer": "mask",
            "type": "fill",
            "paint": {"fill-color": "#333333", "fill-opacity": 0.5},
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
        {
            "id": "box",
            "source": "box",
            "type": "line",
            "paint": {"line-color": "#FF0000", "line-width": 4, "line-opacity": 1},
        },
    ],
}


async def get_locator_map_image(longitude, latitude, bounds):
    """
    Create a rendered locator map image.

    Parameters
    ----------
    latitude : float
        latitude of area of interest marker
    longitude : float
        longitude of area of interest marker
    bounds : list-like of xmin, ymin, xmax, ymax
        bounds of geometry to locate on map

    Returns
    -------
    Image object
    """

    style = deepcopy(LOCATOR_STYLE)

    xmin, ymin, xmax, ymax = bounds

    if xmax - ymax >= 0.5 or ymax - ymin >= 0.5:
        style["sources"]["box"] = {
            "type": "geojson",
            "data": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [xmin, ymin],
                        [xmin, ymax],
                        [xmax, ymax],
                        [xmax, ymin],
                        [xmin, ymin],
                    ]
                ],
            },
        }

    else:
        style["sources"]["marker"] = {
            "type": "geojson",
            "data": {"type": "Point", "coordinates": [longitude, latitude]},
        }

    params = {
        "style": style,
        "center": CENTER,
        "zoom": ZOOM,
        "width": WIDTH,
        "height": HEIGHT,
    }

    try:
        async with httpx.AsyncClient() as client:
            r = await client.post(MBGL_SERVER_URL, json=params)

        if r.status_code != 200:
            log.error(f"Error generating locator image: {r.text[:255]}")
            return None

        return Image.open(BytesIO(r.content))

    except Exception as ex:
        log.error(f"Error generating locator image: {ex}")
        return None
