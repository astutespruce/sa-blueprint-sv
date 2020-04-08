import json

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

    if src_crs == target_crs:
        return geometries.copy()

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


def sjoin(left, right, predicate="intersects", how="left"):
    """Join data frames on geometry, comparable to geopandas.

    NOTE: left vs right must be determined in advance for best performance, unlike geopandas.

    Parameters
    ----------
    left : DataFrame containing pygeos geometry in "geometry" column
    right : DataFrame containing pygeos geometry in "geometry" column
    predicate : str, optional (default "intersects")
    how : str, optional (default "left")

    Returns
    -------
    pandas DataFrame
        Includes all columns from left and all columns from right except geometry, suffixed by _right where
        column names overlap.
    """

    # spatial join is inner to avoid recasting indices to float
    joined = sjoin_geometry(left.geometry, right.geometry, predicate, how="inner")
    joined = left.join(joined, how=how).join(
        right.drop(columns=["geometry"]), on="index_right", rsuffix="_right"
    )
    return joined


def sjoin_geometry(left, right, predicate="intersects", how="inner"):
    """Use pygeos to do a spatial join between 2 series or ndarrays of geometries.

    Parameters
    ----------
    left : Series or ndarray
        left geometries, will form basis of index that is returned
    right : Series or ndarray
        right geometries, their indices will be returned where thy meet predicate
    predicate : str, optional (default: "intersects")
        name of pygeos predicate function (any of the pygeos predicates should work: intersects, contains, within, overlaps, crosses)
    how : str, optional (default: "inner")
        one of "inner" or "left"; "right" is not supported at this time.

    Returns
    -------
    Series
        indexed on index of left, containing values of right index
    """
    if not how in ("inner", "left"):
        raise NotImplementedError("Other join types not implemented")

    if isinstance(left, pd.Series):
        left_values = left.values
        left_index = left.index

    else:
        left_values = left
        left_index = np.arange(0, len(left))

    if isinstance(right, pd.Series):
        right_values = right.values
        right_index = right.index

    else:
        right_values = right
        right_index = np.arange(0, len(right))

    tree = pg.STRtree(right_values)
    # hits are in 0-based indicates of right
    hits = tree.query_bulk(left_values, predicate=predicate)

    if how == "inner":
        index = left_index[hits[0]]
        values = right_index[hits[1]]

    elif how == "left":
        index = left_index.copy()
        values = np.empty(shape=index.shape)
        values.fill(np.nan)
        values[hits[0]] = right_index[hits[1]]

    return pd.Series(values, index=index, name="index_right")


def intersection(left, right):
    """Intersect the geometries from the left with the right.

    New, intersected geometries are stored in "geometry_right".

    Uses spatial index operations for faster operations.  Wholly contained
    geometries from right are copied intact, only those that intersect but are
    not wholly contained are intersected.

    Parameters
    ----------
    left : DataFrame
        pygeos geometry in "geometry" column
    right : DataFrame
        pygeos geometry in "geometry" column

    Returns
    -------
    DataFrame
        output geometries are in "geometry_right"
    """
    intersects = sjoin_geometry(left.geometry, right.geometry)

    if not len(intersects):
        # empty dataframe with correct columns
        return left.join(intersects, how="inner").join(
            right, on="index_right", rsuffix="_right"
        )

    contains = sjoin_geometry(
        left.geometry, right.geometry.iloc[intersects], predicate="contains"
    )

    # any geometries that are completely contained can be copied intact
    out = left.join(contains, how="inner").join(
        right, on="index_right", rsuffix="_right"
    )

    # the remainder need to be intersected
    rest = intersects.loc[~intersects.isin(contains)]

    rest = left.join(rest, how="inner").join(right, on="index_right", rsuffix="_right")
    rest["geometry_right"] = pg.intersection(rest.geometry, rest.geometry_right)

    return out.append(rest, ignore_index=False)


def signed_area(ring):
    """Calculate signed area of a ring.  If positive, is counterclockwise ordering.
    Adapted from shapely::signed_area to numpy

    Parameters
    ----------
    ring : LinearRing

    Returns
    -------
    float
    """

    x, y = pg.get_coordinates(ring).T
    n = x.shape[0]
    y1 = y.take(np.arange(-n + 1, 1))
    y2 = y.take(np.arange(-1, n - 1))
    return (x * (y1 - y2)).sum() / 2.0


# GeoJSON geometry type names
GEOJSON_TYPE = {
    # -1: "", # Not a geometry
    0: "Point",
    1: "LineString",
    2: "LinearRing",  # NOTE: not valid GeoJSON, TODO: could be converted to LineString
    3: "Polygon",
    4: "MultiPoint",
    5: "MultiLineString",
    6: "MultiPolygon",
    7: "GeometryCollection",
}


def to_dict(geometry):
    """Convert pygeos Geometry object to a dictionary representation.
    Equivalent to structure of GeoJSON.

    Parameters
    ----------
    geometry : pygeos Geometry object (singular)

    Returns
    -------
    dict
        GeoJSON dict representation of geometry
    """
    geometry = pg.normalize(geometry)

    def get_ring_coords(polygon):
        # outer ring must be reversed to be counterclockwise[::-1]
        coords = [pg.get_coordinates(pg.get_exterior_ring(polygon)).tolist()]
        for i in range(pg.get_num_interior_rings(polygon)):
            # inner rings must be reversed to be clockwise[::-1]
            coords.append(pg.get_coordinates(pg.get_interior_ring(polygon, i)).tolist())

        return coords

    geom_type = GEOJSON_TYPE[pg.get_type_id(geometry)]
    coords = []

    if geom_type == "MultiPolygon":
        coords = []
        geoms = pg.get_geometry(geometry, range(pg.get_num_geometries(geometry)))
        for geom in geoms:
            coords.append(get_ring_coords(geom))

    elif geom_type == "Polygon":
        coords = get_ring_coords(geometry)

    else:
        raise NotImplementedError("Not built")

    return {"type": geom_type, "coordinates": coords}


def to_json(geometry, *args, **kwargs):
    """Convert a pygeos geometry to GeoJSON.

    Parameters
    ----------
    geometry : pygeos Geometry (singular)

    Returns
    -------
    str
        GeoJSON string
    """
    return json.dumps(to_dict(geometry), *args, **kwargs)


to_dict_all = np.vectorize(to_dict)
to_json_all = np.vectorize(to_json)


def explode(df):
    """Explodes multipart geometries to single parts.  Attributes are copied
    to each individual geometry.

    NOTE: Not yet supported in pygeos, in https://github.com/pygeos/pygeos/pull/130

    Parameters
    ----------
    df : DataFrame

    Returns
    -------
    DataFrame
    """

    ix, parts = pg.get_parts(df.geometry)
    series = pd.Series(parts, index=df.index[ix], name="geometry")

    return df.drop(columns=["geometry"]).join(series)
