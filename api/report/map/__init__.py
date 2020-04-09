import asyncio
import json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

import rasterio

from .aoi import get_aoi_map_image
from .basemap import get_basemap_image
from .locator import get_locator_map_image
from .raster import render_raster, extract_data_for_map
from .summary_unit import get_summary_unit_map_image
from .mercator import get_zoom, get_map_bounds, get_map_scale
from .util import pad_bounds, get_center, to_base64, merge_maps

from constants import BLUEPRINT_COLORS, INDICATORS_INDEX, URBAN_LEGEND, SLR_LEGEND


WIDTH = 740
HEIGHT = 460
PADDING = 5
THREADS = 6


src_dir = Path("data")
blueprint_filename = src_dir / "Blueprint_2_2.tif"
indicators_dir = src_dir / "indicators"
urban_filename = src_dir / "threats/urban/urb_indexed_2060.tif"
slr_filename = src_dir / "threats/slr/slr.vrt"


async def render_mbgl_maps(*args):
    return await asyncio.gather(*args)


def render_raster_map(bounds, scale, basemap_image, aoi_image, id, path, colors):
    raster_img = render_raster(path, bounds, scale, WIDTH, HEIGHT, colors)

    map_image = None
    if raster_img is not None:
        map_image = merge_maps([basemap_image, raster_img, aoi_image])
        map_image = to_base64(map_image)

    return id, map_image


async def render_raster_maps(
    bounds, scale, basemap_image, aoi_image, indicators, urban, slr
):
    executor = ThreadPoolExecutor(max_workers=THREADS)
    loop = asyncio.get_event_loop()

    base_args = (bounds, scale, basemap_image, aoi_image)

    task_args = [("blueprint", blueprint_filename, BLUEPRINT_COLORS)]

    for id in indicators:
        indicator = INDICATORS_INDEX[id]
        task_args.append(
            (id, indicators_dir / indicator["filename"], indicator["colors"])
        )

    if urban:
        colors = {i: e["color"] for i, e in enumerate(URBAN_LEGEND) if e is not None}
        task_args.append(("urban", urban_filename, colors))

    if slr:
        colors = {i: e["color"] for i, e in enumerate(SLR_LEGEND)}
        task_args.append(("slr", slr_filename, colors))

    # NOTE: have to have handle on pending or task loop gets closed too soon
    completed, pending = await asyncio.wait(
        [
            loop.run_in_executor(executor, render_raster_map, *base_args, *args)
            for args in task_args
        ]
    )

    results = [t.result() for t in completed]
    maps = {k: v for k, v in results if v is not None}

    return maps


async def render_maps(
    bounds, geometry=None, summary_unit_id=None, indicators=None, urban=False, slr=False
):
    """Render maps for locator and each raster dataset that overlaps with area
    of interest.

    Parameters
    ----------
    bounds : list-like of [xmin, ymin, xmax, ymax]
        bounds of area of interest, will be used to derive map bounds.
    geometry : pygeos.Geometry, optional (default: None)
        If present, will be used to render the area of interest
    summary_unit_id : [type], optional (default: None)
        If present, will be used to identify the selected summary unit
    indicators : list-like, optional (default: None)
        If present, is a list of all indicator IDs to render.
    urban : bool, optional (default: False)
        If True, urban will be rendered.
    slr : bool, optional (default: False)
        If True, sea level rise will be rendered.

    Returns
    -------
    dict
        Dictionary of map IDs to base64 data
    """

    maps = {}

    bounds = pad_bounds(bounds, PADDING)
    center = get_center(bounds)
    zoom = get_zoom(bounds, WIDTH, HEIGHT)

    bounds = get_map_bounds(center, zoom, WIDTH, HEIGHT)
    scale = get_map_scale(bounds, WIDTH)

    if geometry:
        aoi_task = get_aoi_map_image(geometry, center, zoom, WIDTH, HEIGHT)

    elif summary_unit_id:
        aoi_task = get_summary_unit_map_image(
            summary_unit_id, center, zoom, WIDTH, HEIGHT
        )

    tasks = [
        get_locator_map_image(*center, bounds=bounds),
        get_basemap_image(center, zoom, WIDTH, HEIGHT),
        aoi_task,
    ]

    locator_image, basemap_image, aoi_image = await render_mbgl_maps(*tasks)

    maps["locator"] = to_base64(locator_image)

    # make sure that images are fully loaded before sending to other threads
    if basemap_image is not None:
        basemap_image.load()

    if aoi_image is not None:
        aoi_image.load()

    # Use background threads for rendering rasters
    raster_maps = await render_raster_maps(
        bounds, scale, basemap_image, aoi_image, indicators or [], urban, slr
    )

    maps.update(raster_maps)

    return maps, scale
