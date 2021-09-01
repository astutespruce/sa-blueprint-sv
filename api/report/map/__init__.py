import asyncio
import json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

import rasterio

from .aoi import get_aoi_map_image
from .basemap import get_basemap_image
from .locator import get_locator_map_image
from .ownership import get_ownership_map_image
from .protection import get_protection_map_image
from .raster import render_raster, extract_data_for_map
from .summary_unit import get_summary_unit_map_image
from .mercator import get_zoom, get_map_bounds, get_map_scale
from .util import pad_bounds, get_center, to_base64, merge_maps

from analysis.constants import (
    BLUEPRINT_COLORS,
    CORRIDORS_COLORS,
    INDICATOR_INDEX,
    URBAN_LEGEND,
    SLR_LEGEND,
    CORRIDORS,
)
from api.settings import MAP_RENDER_THREADS


WIDTH = 740
HEIGHT = 440
PADDING = 5


src_dir = Path("data/inputs")
indicators_dir = src_dir / "indicators"
blueprint_filename = src_dir / "blueprint2021.tif"
corridors_filename = src_dir / "corridors.tif"
urban_filename = src_dir / "threats/urban/urban_2060.tif"
slr_filename = src_dir / "threats/slr/slr.vrt"


async def render_mbgl_maps(**kwargs):
    """Asynchronously render MBGL maps based on number of MAP_RENDER_THREADS

    Returns
    -------
    dict, dict
        tuple of (maps, errors) keyed by map ID
    """
    results = await asyncio.gather(*kwargs.values())
    results = zip(kwargs.keys(), results)

    maps = {}
    errors = {}
    for key, (map, error) in results:
        maps[key] = map
        if error is not None:
            errors[key] = error

    return maps, errors


def render_raster_map(bounds, scale, basemap_image, aoi_image, id, path, colors):
    """Render raster dataset map based on bounds.  Merge this over basemap image
    and under aoi_image.

    Parameters
    ----------
    bounds : list-like of [xmin, ymin, xmax, ymax]
        bounds of map
    scale : dict
        map scale info
    basemap_image : Image object
    aoi_image : Image object
    id : str
        map ID
    path : str
        path to raster dataset
    colors : list-like of colors
        colors to render map image based on values in raster

    Returns
    -------
    id, Image object
        Image object is None if it could not be rendered or does not overlap bounds
    """
    raster_img = render_raster(path, bounds, scale, WIDTH, HEIGHT, colors)
    map_image = merge_maps([basemap_image, raster_img, aoi_image])
    map_image = to_base64(map_image)

    return id, map_image


async def render_raster_maps(
    bounds, scale, basemap_image, aoi_image, indicators, urban, slr
):
    """Asynchronously render Raster maps.

    Parameters
    ----------
    bounds : list-like of [xmin, ymin, xmax, ymax]
        bounds of map
    scale : dict
        map scale info
    basemap_image : Image object
    aoi_image : Image object
    indicators : list-like of indicator IDs
    urban : bool (default False)
        if True, will render urban map
    slr : bool (default False)
        if True, will render SLR map

    Returns
    -------
    dict, dict
        tuple of (maps, errors) keyed by map ID
    """
    executor = ThreadPoolExecutor(max_workers=MAP_RENDER_THREADS)
    loop = asyncio.get_event_loop()

    base_args = (bounds, scale, basemap_image, aoi_image)

    task_args = [
        ("blueprint", blueprint_filename, BLUEPRINT_COLORS),
        ("corridors", corridors_filename, CORRIDORS_COLORS),
    ]

    for id in indicators:
        indicator = INDICATOR_INDEX[id]
        colors = {
            e["value"]: e["color"]
            for e in indicator["values"]
            if e["color"] is not None
        }
        task_args.append((id, indicators_dir / indicator["filename"], colors))

    if urban:
        colors = {i: e["color"] for i, e in enumerate(URBAN_LEGEND) if e is not None}
        task_args.append(("urban_2060", urban_filename, colors))

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

    # TODO: capture and return errors
    errors = {}

    return maps, errors


async def render_maps(
    bounds,
    geometry=None,
    summary_unit_id=None,
    indicators=None,
    urban=False,
    slr=False,
    ownership=False,
    protection=False,
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
    ownership : bool, optional (default: False)
        If True, ownership will be rendered.
    protection : bool, optional (default: False)
        If True, ownership will be rendered.

    Returns
    -------
    dict
        Dictionary of map IDs to base64 data
    """

    maps = {}
    errors = {}

    bounds = pad_bounds(bounds, PADDING)
    center = get_center(bounds)
    zoom = get_zoom(bounds, WIDTH, HEIGHT)

    bounds = get_map_bounds(center, zoom, WIDTH, HEIGHT)
    scale = get_map_scale(bounds, WIDTH)

    tasks = {
        "locator": get_locator_map_image(*center, bounds=bounds, geometry=geometry),
        "basemap": get_basemap_image(center, zoom, WIDTH, HEIGHT),
    }

    if geometry:
        tasks["aoi"] = get_aoi_map_image(geometry, center, zoom, WIDTH, HEIGHT)

    elif summary_unit_id:
        tasks["aoi"] = get_summary_unit_map_image(
            summary_unit_id, center, zoom, WIDTH, HEIGHT
        )

    if ownership:
        tasks["ownership"] = get_ownership_map_image(center, zoom, WIDTH, HEIGHT)

    if protection:
        tasks["protection"] = get_protection_map_image(center, zoom, WIDTH, HEIGHT)

    mbgl_maps, mbgl_map_errors = await render_mbgl_maps(**tasks)
    errors.update(mbgl_map_errors)

    maps["locator"] = to_base64(mbgl_maps["locator"])
    basemap_image = mbgl_maps.get("basemap", None)
    aoi_image = mbgl_maps.get("aoi", None)

    ownership_image = mbgl_maps.get("ownership", None)
    if ownership_image is not None:
        maps["ownership"] = to_base64(
            merge_maps([basemap_image, mbgl_maps["ownership"], aoi_image])
        )

    protection_image = mbgl_maps.get("protection", None)
    if protection_image is not None:
        maps["protection"] = to_base64(
            merge_maps([basemap_image, mbgl_maps["protection"], aoi_image])
        )

    # Use background threads for rendering rasters
    raster_maps, raster_map_errors = await render_raster_maps(
        bounds, scale, basemap_image, aoi_image, indicators or [], urban, slr
    )

    maps.update(raster_maps)
    errors.update(raster_map_errors)

    return maps, scale, errors
