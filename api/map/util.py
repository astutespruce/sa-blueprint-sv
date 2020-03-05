import math


def get_center(bounds):
    """
    Calculate center point from bounds in longitude, latitude format.

    Parameters
    ----------
    bounds : list-like of (west, south, east, north) in geographic coordinates
        geographic bounds of the map

    Returns
    -------
    list: [longitude, latitude]
    """

    return [
        ((bounds[2] - bounds[0]) / 2.0) + bounds[0],
        ((bounds[3] - bounds[1]) / 2.0) + bounds[1],
    ]


def pad_bounds(bounds, percent=0):
    """Pad the bounds by a percentage

    Parameters
    ----------
    bounds : list-like of (west, south, east, north)
    percent : int, optional
        percent to pad the bounds

    Returns
    -------
    (west, south, east, north)
    """

    xmin, ymin, xmax, ymax = bounds
    x_pad = (xmax - xmin) * (percent / 100)
    y_pad = (ymax - ymin) * (percent / 100)

    return [xmin - x_pad, ymin - y_pad, xmax + x_pad, ymax + y_pad]


def to_geojson(series):
    """Return a GeoJSON geometry collection from the series (must be in EPSG:4326).
    Did not use the builtin for the series since it introduces a lot of bloat.
    """

    return {
        "type": "GeometryCollection",
        "geometries": series.apply(lambda x: x.__geo_interface__).to_list(),
    }

