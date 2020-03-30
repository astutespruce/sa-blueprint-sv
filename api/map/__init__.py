import json
from pathlib import Path

import rasterio

from api.map.aoi import get_aoi_map_image
from api.map.basemap import get_basemap_image
from api.map.locator import get_locator_map_image
from api.map.raster import render_raster, extract_data_for_map
from api.map.summary_unit import get_summary_unit_map_image
from api.map.util import pad_bounds, get_center, to_base64, merge_maps
from api.map.mercator import get_zoom, get_map_bounds

from constants import BLUEPRINT_COLORS, INDICATORS_INDEX


WIDTH = 740
HEIGHT = 500
PADDING = 5


src_dir = Path("data")
blueprint_filename = src_dir / "Blueprint_2_2.tif"


# TODO: pass in list of indicators that had data
# TODO: SLR, urbanization
def render_maps(bounds, geojson=None, summary_unit_id=None, indicators=None):
    maps = {}

    bounds = pad_bounds(bounds, PADDING)
    center = get_center(bounds)
    zoom = get_zoom(bounds, WIDTH, HEIGHT)

    locator = get_locator_map_image(*center)
    maps["locator"] = to_base64(locator)

    bounds = get_map_bounds(center, zoom, WIDTH, HEIGHT)

    # get basemap image
    basemap_image = get_basemap_image(center, zoom, WIDTH, HEIGHT)

    aoi_image = None

    if geojson:
        # get AOI image
        aoi_image = get_aoi_map_image(geojson, center, zoom, WIDTH, HEIGHT)

    elif summary_unit_id:
        aoi_image = get_summary_unit_map_image(
            summary_unit_id, center, zoom, WIDTH, HEIGHT
        )

    with rasterio.open(blueprint_filename) as src:
        data = extract_data_for_map(src, bounds, WIDTH, HEIGHT)
        raster_img = None
        if data is not None:
            raster_img = render_raster(data, BLUEPRINT_COLORS, src.nodata)

        map_image = merge_maps([basemap_image, raster_img, aoi_image])
        maps["blueprint"] = to_base64(map_image)

    if indicators is not None:
        for id in indicators:
            indicator = INDICATORS_INDEX[id]
            # print("Processing map for", id)

            with rasterio.open(src_dir / "indicators" / indicator["filename"]) as src:
                data = extract_data_for_map(src, bounds, WIDTH, HEIGHT)

                raster_img = None
                if data is not None:
                    raster_img = render_raster(data, indicator["colors"], src.nodata)
                    map_image = merge_maps([basemap_image, raster_img, aoi_image])
                    maps[id] = to_base64(map_image)

                else:
                    print("Only nodata...")

    return maps
