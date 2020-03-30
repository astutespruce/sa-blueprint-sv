import geopandas as gp
import numpy as np
import pandas as pd
import pygeos as pg
from pyproj.transformer import Transformer
from shapely.wkb import loads


def to_crs(geometries, src_crs, target_crs):
    """Convert coordinates from one CRS to another CRS

    Parameters
    ----------
    geometries : ndarray of pygeos geometries
    src_crs : CRS or params to create it
    target_crs : CRS or params to create it
    """

    transformer = Transformer.from_crs(src_crs, target_crs, always_xy=True)
    coords = pg.get_coordinates(geometries)
    new_coords = transformer.transform(coords[:, 0], coords[:, 1])
    result = pg.set_coordinates(geometries.copy(), np.array(new_coords).T)
    return result


def to_pygeos(geometries):
    """Convert GeoPandas geometries to pygeos geometries

    Parameters
    ----------
    geometries : GeoSeries

    Returns
    -------
    ndarray of pygeos geometries
    """
    return pg.from_wkb(geometries.apply(lambda g: g.to_wkb()))


def from_pygeos(geometries):
    """Converts a Series or ndarray of pygeos geometry objects to a GeoSeries.

    Parameters
    ----------
    geometries : Series or ndarray of pygeos geometry objects

    Returns
    -------
    GeoSeries
    """

    def load_wkb(wkb):
        return loads(wkb)

    wkb = pg.to_wkb(geometries)

    if isinstance(geometries, pd.Series):
        return gp.GeoSeries(wkb.apply(load_wkb))

    return gp.GeoSeries(np.vectorize(load_wkb, otypes=[np.object])(wkb))
