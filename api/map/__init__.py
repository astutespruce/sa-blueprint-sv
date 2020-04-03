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

from constants import BLUEPRINT_COLORS, INDICATORS_INDEX, URBAN_LEGEND, SLR_LEGEND


WIDTH = 740
HEIGHT = 480
PADDING = 5


src_dir = Path("data")
blueprint_filename = src_dir / "Blueprint_2_2.tif"
urban_filename = src_dir / "threats/urban/urb_indexed_2060.tif"
slr_filename = src_dir / "threats/slr/slr.vrt"


# TODO: SLR, urbanization
def render_maps(
    bounds, geometry=None, summary_unit_id=None, indicators=None, urban=False, slr=False
):
    maps = {}

    bounds = pad_bounds(bounds, PADDING)
    center = get_center(bounds)
    zoom = get_zoom(bounds, WIDTH, HEIGHT)

    locator = get_locator_map_image(*center, bounds=bounds)
    maps["locator"] = to_base64(locator)

    bounds = get_map_bounds(center, zoom, WIDTH, HEIGHT)

    # get basemap image
    basemap_image = get_basemap_image(center, zoom, WIDTH, HEIGHT)

    aoi_image = None

    if geometry:
        # get AOI image
        aoi_image = get_aoi_map_image(geometry, center, zoom, WIDTH, HEIGHT)

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

            with rasterio.open(src_dir / "indicators" / indicator["filename"]) as src:
                data = extract_data_for_map(src, bounds, WIDTH, HEIGHT)

                raster_img = None
                if data is not None:
                    raster_img = render_raster(data, indicator["colors"], src.nodata)
                    map_image = merge_maps([basemap_image, raster_img, aoi_image])
                    maps[id] = to_base64(map_image)

    if urban:
        with rasterio.open(urban_filename) as src:
            data = extract_data_for_map(src, bounds, WIDTH, HEIGHT)

            raster_img = None
            if data is not None:
                colors = {i: e["color"] for i, e in enumerate(URBAN_LEGEND)}
                # 0 = not urban nor predicted to be, make it transparent
                raster_img = render_raster(data, colors, 0)
                map_image = merge_maps([basemap_image, raster_img, aoi_image])
                maps["urban_2060"] = to_base64(map_image)

    if slr:
        with rasterio.open(slr_filename) as src:
            data = extract_data_for_map(src, bounds, WIDTH, HEIGHT)

            raster_img = None
            if data is not None:
                colors = {i: e["color"] for i, e in enumerate(SLR_LEGEND)}
                raster_img = render_raster(data, colors, src.nodata)
                map_image = merge_maps([basemap_image, raster_img, aoi_image])
                maps["slr"] = to_base64(map_image)

    return maps
