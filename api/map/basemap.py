from io import BytesIO

import httpx
from PIL import Image


from settings import MBGL_SERVER_URL

STYLE = {
    "version": 8,
    "sources": {
        "basemap": {
            "type": "raster",
            "tiles": [
                "https://services.arcgisonline.com/arcgis/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}"
            ],
            "tileSize": 256,
        }
    },
    "layers": [{"id": "basemap", "type": "raster", "source": "basemap"}],
}


def get_basemap_image(center, zoom, width, height):
    """Create a rendered map image of the basemap.

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

    r = httpx.post(MBGL_SERVER_URL, json=params)
    return Image.open(BytesIO(r.content))

