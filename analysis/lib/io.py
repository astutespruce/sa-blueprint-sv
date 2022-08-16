import numpy as np
import rasterio


def write_raster(filename, data, transform, crs, nodata, **kwargs):
    """Write data to a GeoTIFF.

    Parameters
    ----------
    filename : str
    data : d ndarray
    transform : rasterio transform object
    crs : rasterio.crs object
    nodata : int
    """

    count = 1 if len(data.shape) == 2 else data.shape[-1]

    meta = {
        "driver": "GTiff",
        "dtype": data.dtype,
        "nodata": nodata,
        "width": data.shape[1],
        "height": data.shape[0],
        "count": count,
        "crs": crs,
        "transform": transform,
        "compress": "lzw",
        "tiled": True,
        "blockxsize": 256,
        "blockysize": 256,
    }

    if kwargs:
        meta.update(kwargs)

    with rasterio.open(filename, "w", **meta) as out:
        if count == 1:
            out.write(data, indexes=1)
        else:
            # rework from row, col, z to z,row, col
            out.write(np.rollaxis(data, axis=-1))
