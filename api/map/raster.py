from affine import Affine
import numpy as np

from PIL import Image
import rasterio
from rasterio.enums import Resampling
from rasterio.mask import raster_geometry_mask
from rasterio import windows
from rasterio.warp import (
    transform_bounds,
    transform as transform_coords,
    calculate_default_transform,
    reproject,
)

from tilecutter.rgb import hex_to_rgb
from tilecutter.png import to_paletted_png

from constants import DATA_CRS, MAP_CRS, GEO_CRS, DEBUG
from api.map.io import write_raster


def extract_data_for_map(src, bounds, map_width, map_height, densify=4):
    """Extract, reproject, and clip data within bounds for map images.

    Returns None if there is only nodata within the bounds.

    Parameters
    ----------
    src : rasterio.RasterReader
        open rasterio reader
    bounds : list-like of (west, south, east, north)
    map_width : int
    map_height : int
    densify : int, optional (default 4)
        Amount to densify pixels during reprojection.  A higher number more closely
        approximates original pixels but has higher memory and performance costs.

    Returns
    -------
    2d ndarray or None
    """

    src_crs = src.crs

    # Project bounds and define window to extract data.
    # Round it to align with pixels
    window = (
        src.window(*transform_bounds(GEO_CRS, DATA_CRS, *bounds, densify_pts=21))
        .round_offsets(op="floor")
        .round_lengths(op="ceil")
    )
    # expand by 1px on all sides to be safe
    window = windows.Window(
        window.col_off - 1, window.row_off - 1, window.width + 2, window.height + 2
    )

    window_bounds = src.window_bounds(window)
    window_transform = src.window_transform(window)

    # Read data in window, potentially beyond extent of data
    # TODO: https://github.com/mapbox/rasterio/issues/1878
    # int8 nodata is not handled correctly and is converted to 0 instead
    # TEMP: reassign nodata value internally
    nodata = src.nodata
    if src.dtypes[0] == "int8" and src.nodata == -128:
        nodata = 127

    data = src.read(1, window=window, boundless=True, fill_value=nodata)

    if DEBUG:
        write_raster("/tmp/pre-warp.tif", data, window_transform, src.crs, nodata)

    # convert data before reproject
    if nodata != src.nodata:
        data[data == src.nodata] = nodata

    if not np.any(data != nodata):
        # entire area is nodata, no point in warping nodata pixels
        return None

    # Calculate initial transform to project to Spherical Mercator
    src_height, src_width = data.shape
    proj_transform, proj_width, proj_height = calculate_default_transform(
        src.crs,
        MAP_CRS,
        src_width,
        src_height,
        *window_bounds,
        dst_width=map_width * densify,
        dst_height=map_height * densify,
    )

    # Project to Spherical Mercator
    projected = np.empty(shape=(proj_height, proj_width), dtype=data.dtype)
    reproject(
        source=data,
        destination=projected,
        src_transform=window_transform,
        src_crs=src_crs,
        src_nodata=nodata,
        dst_transform=proj_transform,
        dst_crs=MAP_CRS,
        dst_nodata=nodata,
        resampling=Resampling.nearest,
    )

    # Clip to bounds after reprojection
    clip_window = (
        windows.from_bounds(
            *transform_bounds(GEO_CRS, MAP_CRS, *bounds), proj_transform
        )
        .round_offsets(op="floor")
        .round_lengths(op="ceil")
    )
    clip_transform = windows.transform(clip_window, proj_transform)

    # read projected data within window
    data = projected[clip_window.toslices()]
    height, width = data.shape

    scaling = Affine.scale(width / map_width, height / map_height)
    final_transform = clip_transform * scaling

    clipped = np.empty(shape=(map_height, map_width), dtype=data.dtype)
    reproject(
        source=data,
        destination=clipped,
        src_transform=clip_transform,
        src_crs=MAP_CRS,
        dst_transform=final_transform,
        dst_crs=MAP_CRS,
        resampling=Resampling.nearest,
    )

    if DEBUG:
        write_raster(
            "/tmp/warped-clipped.tif", clipped, final_transform, MAP_CRS, nodata
        )

    # TEMP: Strip nodata values back out
    if nodata != src.nodata:
        clipped[clipped == nodata] = src.nodata

    return clipped


def render_raster(data, colors, nodata):
    num_colors = max(colors.keys())
    nodata_index = num_colors + 1

    # TODO: probably a much easier way to create RGBA from colors using numpy
    # alpha is 0 for transparent and <= 255 for opaque parts

    # convert nodata
    data[data == nodata] = nodata_index
    # create palette and set missing indexes to nodata index
    palette = []
    for i in range(0, num_colors + 1):
        if i in colors:
            palette.append(hex_to_rgb(colors[i]))
        else:
            # convert pixel value to nodata
            data[data == i] = nodata_index
            palette.append((0, 0, 0))

    # add nodata color to palette (set as transparent below)
    palette.append((0, 0, 0))

    img = Image.frombuffer("P", (data.shape[1], data.shape[0]), data, "raw", "P", 0, 1)
    # palette must be a list of [r, g, b, r, g, b, ...]  values
    img.putpalette(np.array(palette, dtype="uint8").flatten().tolist(), "RGB")
    img.info["transparency"] = nodata_index

    # Convert to RGBA and putalpha to set transparency
    img = img.convert("RGBA")

    # can also putalpha with a mask made from L img instead of a single value
    # might be able to forgo setting alpha above?

    # Convert to part transparent
    arr = np.array(img)
    a = arr[:, :, 3]
    a[a == 255] = 175  # set alpha value to part transparent

    img = Image.fromarray(arr)

    return img
