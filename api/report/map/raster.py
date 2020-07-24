from affine import Affine
import math
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


from analysis.constants import DATA_CRS, MAP_CRS, GEO_CRS, DEBUG
from analysis.io import write_raster


def hex_to_rgb(color):
    """Convert a hex color code to an 8 bit rgb tuple.

    Parameters
    ----------
    color : string, must be in #112233 syntax

    Returns
    -------
    tuple : (red, green, blue) as 8 bit numbers

    """

    if not len(color) == 7 and color[0] == "#":
        raise ValueError("Color must be in #112233 format")

    color = color.lstrip("#")

    return tuple(int(color[i : i + 2], 16) for i in (0, 2, 4))


def extract_data_for_map(src, bounds, scale, map_width, map_height):
    """Extract, reproject, and clip data within bounds for map images.

    Returns None if there is only nodata within the bounds.

    Parameters
    ----------
    src : rasterio.RasterReader
        open rasterio reader
    bounds : list-like of (west, south, east, north)
    scale : dict
        contains resolution of map image pixels
    map_width : int
    map_height : int

    Returns
    -------
    2d ndarray or None
    """

    src_crs = src.crs

    # Densify between 1 and 4 raster pixels per screen pixel.
    # Higher densification is needed where the bounds cover a small number of pixels
    # in the output map
    densify = max(1, min(4, math.ceil(src.res[0] / scale["resolution"])))

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

    # if DEBUG:
    #     write_raster("/tmp/pre-warp.tif", data, window_transform, src.crs, nodata)

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

    # if DEBUG:
    #     write_raster(
    #         "/tmp/warped-clipped.tif", clipped, final_transform, MAP_CRS, nodata
    #     )

    # TEMP: Strip nodata values back out
    if nodata != src.nodata:
        clipped[clipped == nodata] = src.nodata

    return clipped


def render_array(data, colors):
    """Render a data array to a PIL Image.

    Data values must be indexes into colors.

    Parameters
    ----------
    data : 2D array
        Values must be indexes into colors.  Any value not present in colors
        is rendered as completely transparent.
    colors : dict of hex colors
        lookup table of pixel values to colors

    Returns
    -------
    PIL Image
    """

    # fully transparent image by default
    # alpha is 0 for transparent and <= 255 for opaque parts
    rgba = np.zeros(shape=data.shape + (4,), dtype="uint8")

    for i, color in colors.items():
        r, g, b = hex_to_rgb(color)
        a = 175

        rgba[data == i, :] = r, g, b, a

    return Image.fromarray(rgba, "RGBA")


def render_raster(path, bounds, scale, width, height, colors):
    """Render a raster dataset to a PIL Image.

    Parameters
    ----------
    path : str or pathlib.Path
    bounds : list-like of [xmin, ymin, xmax, ymax]
        Map bounds
    width : int
    height : int
    colors : dict of hex colors
        lookup table of pixel values to colors

    Returns
    -------
    PIL Image
    """
    with rasterio.open(path) as src:
        data = extract_data_for_map(src, bounds, scale, width, height)

        if data is not None:
            # does not overlap with bounds
            return render_array(data, colors)

        return None
