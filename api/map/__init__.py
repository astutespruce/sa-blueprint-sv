from PIL import Image

from api.map.aoi import get_aoi_map_image
from api.map.basemap import get_basemap_image
from api.map.locator import get_locator_map_image
from api.map.raster import render_raster


def merge_maps(basemap, raster, aoi):
    img = basemap.copy()
    img = Image.alpha_composite(img, raster)
    img = Image.alpha_composite(img, aoi)

    return img
