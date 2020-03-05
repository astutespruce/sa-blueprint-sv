import math


R2D = 180 / math.pi
D2R = math.pi / 180
A = 6378137.0


def to_mercator(longitude, latitude):
    """Convert longitude, latitude to Spherical Mercator.

    Ported from mercantile.

    Parameters
    ----------
    longitude : float
    latitude : float

    Returns
    -------
    (x, y)
    """

    x = A * math.radians(longitude)
    if latitude <= -90:
        y = float("-inf")
    elif lat >= 90:
        y = float("inf")
    else:
        y = A * math.log(math.tan((math.pi * 0.25) + (0.5 * math.radians(latitude))))
    return x, y


def from_mercator(x, y):
    """Convert x,y coordinate from Spherical Mercator to lon, lat

    Ported from mercantile.

    Parameters
    ----------
    x : float
    y : float

    Returns
    -------
    (longitude, latitude)
    """

    return (x * R2D / A, ((math.pi * 0.5) - 2.0 * math.atan(math.exp(-y / A))) * R2D)


def to_tile_px(longitude, latitude, zoom, tile_size=256):
    """Calculate Spherical Mercator tile x,y coordinate for

    Ported from JS: @mapbox/sphericalmercator.

    Parameters
    ----------
    longitude : float
    latitude : float
    zoom : float
        target zoom level in which to calculate coordinates
    tile_size : int, optional (default 256)

    Returns
    -------
    (x,y)
    """

    size = tile_size * math.pow(2, zoom)
    zc = size / 2
    bc = size / 360
    cc = size / (2 * math.pi)
    f = min(max(math.sin(D2R * latitude), -0.9999), 0.9999)
    x = zc + longitude * bc
    y = zc + 0.5 * math.log((1 + f) / (1 - f)) * -cc

    if x > size:
        x = size
    if y > size:
        y = size

    return x, y


def from_tile_px(x, y, zoom, tile_size=256):
    """Convert from tile pixel coordinates at a zoom level to longitude, latitude.

    Parameters
    ----------
    x : float
        x value in tile pixel coordinates at zoom level
    y : float
        y value in tile pixel coordinates at zoom level
    zoom : float
        zoom level for tile coordinates
    tile_size : int, optional (default 256)

    Returns
    -------
    (longitude, latitude)
    """
    size = tile_size * math.pow(2, zoom)
    zc = size / 2
    bc = size / 360
    cc = size / (2 * math.pi)
    g = (y - zc) / -cc
    longitude = (x - zc) / bc
    latitude = R2D * (2 * math.atan(math.exp(g)) - 0.5 * math.pi)

    return longitude, latitude


def get_zoom(bounds, target_width, target_height):
    """Calculate zoom that fits bounds to the requested image dimensions.

    Ported from JS: @mapbox/geo-viewport.

    Parameters
    ----------
    bounds : list-like of (west, south, east, north) in geographic coordinates
    target_width : int
        target image width
    target_height : int
        target image height

    Returns
    -------
    zoom : float
    """

    base_zoom = 20
    bl = to_tile_px(*bounds[:2], base_zoom)
    tr = to_tile_px(*bounds[2:], base_zoom)
    width = tr[0] - bl[0]
    height = bl[1] - tr[1]
    width_ratio = width / target_width
    height_ratio = height / target_height

    zoom = min(
        base_zoom - (math.log(width_ratio) / math.log(2)),
        base_zoom - (math.log(height_ratio) / math.log(2)),
    )

    zoom = max(zoom - 1, 0)

    return zoom


def get_bounds(center_longitude, center_latitude, zoom, width, height):
    """Calculate bounds of image based on center and zoom.

    Parameters
    ----------
    center_longitude : float
    center_latitude : float
    zoom : float
        zoom level at which tiles will be rendered in map
    width : int
        image width in pixels
    height : int
        image height in pixels

    Returns
    -------
    (west, south, east, north)
    """
    half_width = width / 2
    half_height = height / 2

    cx, cy = to_tile_px(center_longitude, center_latitude, zoom)

    left = cx - half_width
    right = cx + half_width

    # Note: tile coordinates are flipped in y direction
    bottom = cy + half_height
    top = cy - half_height

    west, south = from_tile_px(left, bottom, zoom)
    east, north = from_tile_px(right, top, zoom)

    return west, south, east, north
