/* eslint-disable no-bitwise */
/* eslint-disable no-underscore-dangle */

import { arrayToObject } from 'util/data'
import { indicatorSources } from './mapConfig'

/**
 * Calculate a Mapbox GL JS tile key to use for querying the tile cache.
 * Adapted from mapbox-gl-js::tile_id.js::calculateKey and other functions / classes
 * and simplified for no wrap or overscaledZ.
 * @param {number} zoom
 * @param {number} mercX - mercator X coordinate
 * @param {number} mercY - mercator Y coordinate
 * @returns
 */
const calculateTileKey = (zoom, mercX, mercY) => {
  const tiles = 1 << zoom
  const x = Math.floor(mercX * tiles)
  const y = Math.floor(mercY * tiles)
  const dim = 1 << Math.min(zoom, 22)
  const xy = dim * (+y % dim) + (+x % dim)
  const key = (xy * 32 + zoom) * 16
  return key
}

/**
 * Find the first available loaded tile starting from max zoom
 * @param {Object} cache - tile cache object
 * @param {number} maxzoom - max zoom to start search
 * @param {number} minzoom - min zoom to end search
 * @param {number} mercX - mercator X coordinate
 * @param {number} mercY - mercator Y coordinate
 * @returns Tile or null
 */
const findLoadedTile = (cache, maxzoom, minzoom, mercX, mercY) => {
  for (let z = maxzoom; z >= minzoom; z -= 1) {
    const key = calculateTileKey(z, mercX, mercY)
    const tile = cache[key]
    if (tile && tile.hasData()) {
      return tile
    }
  }
  return null
}

/**
 * Extracts RGB data from a pixel at a location, encoded as a uint32 value.
 * Returns null if data is not yet loaded or point is outside bounds for
 * available tiles.
 * @param {Object} map - mapbox GL map object
 * @param {Object} point - {lat, lng} of point for which to extract pixel data
 * @param {String} layerId - layer from which to extract pixel data
 */
export const getPixelValue = (map, point, layerId) => {
  // TODO: pass in screen point as param instead
  const screenPoint = map.project(point)

  const sourceCache = map.style._otherSourceCaches[layerId]

  if (!sourceCache) {
    // console.error('map source cache not available for', layerId)
    return null
  }

  const { transform } = sourceCache
  const { minzoom, maxzoom } = sourceCache.getSource()

  // also mostly equivalent to transform.locationCoordinate(point)
  // both return mercator coords
  const { x, y } = transform.pointCoordinate(screenPoint)

  // first, try to get tile for the current zoom level since this is called
  // after tiles should have loaded
  const tileKey = calculateTileKey(Math.floor(map.getZoom()), x, y)
  let tile = sourceCache._tiles[tileKey]

  // if we don't have a tile at the current zoom, look for other tiles in the
  // cache
  if (!(tile && tile.hasData())) {
    tile = findLoadedTile(sourceCache._tiles, maxzoom, minzoom, x, y)
  }

  if (!tile) {
    // console.debug(`No tiles in ${layerId} available for point`)
    return null
  }

  if (!(tile.texture && tile.texture.texture)) {
    // console.debug(`Tile image not yet loaded ${tile.tileID.toString()}`)
    return null
  }

  // NOTE: raw tiles may be smaller images than they claim to be in the
  // layer tileSize property (they are overzoomed)
  const tileSize = tile.texture.size[0]

  // rescale Mercator coordinates to tile coords
  const {
    tileTransform: { scale, x: tfX, y: tfY },
  } = tile
  const tileX = Math.floor((x * scale - tfX) * tileSize)
  const tileY = Math.floor((y * scale - tfY) * tileSize)

  if (tileX < 0 || tileY < 0 || tileX > tileSize || tileY > tileSize) {
    // console.debug(`Outside bounds of tile ${tile.tileID.toString()}`)
    return null
  }

  // console.debug(
  //   `Extracting data for tile ${tile.tileID.toString()},  coords: x:${tileX}, y:${tileY}`
  // )

  const {
    painter: {
      context: { gl },
    },
  } = map
  const fb = gl.createFramebuffer()
  gl.bindFramebuffer(gl.FRAMEBUFFER, fb)
  gl.framebufferTexture2D(
    gl.FRAMEBUFFER,
    gl.COLOR_ATTACHMENT0,
    gl.TEXTURE_2D,
    tile.texture.texture,
    0
  )

  const pixels = new Uint8Array(4)
  gl.readPixels(tileX, tileY, 1, 1, gl.RGBA, gl.UNSIGNED_BYTE, pixels)

  // release framebuffer
  gl.bindFramebuffer(gl.FRAMEBUFFER, null)
  gl.deleteFramebuffer(fb)

  // decode to uint
  const [r, g, b] = pixels
  const value = (r << 16) | (g << 8) | b
  // console.debug('pixels', pixels, '==>', value)

  return value
}

/**
 * Decode a uint32 value containing encoded bit-level data according to encoding.
 * Returns null if value is null or 0 (all layers absent)
 * Otherwise returns [{id: <layer id>, value: <decoded value>}, ...]
 * @param {number} value - uint32 encoded RGB value
 * @param {Object} encoding - object that provides:
 * {
 *    bits: <total bits used>,
 *    layers: [{id: <layer id>, bits: <bits used by layer>}]
 * }
 */
export const decodeBits = (value, encoding) => {
  // if value is 0, that means pixel was entirely nodata for all layers
  if (value === null || value === 0) {
    return null
  }

  const { bits: totalBits, layers } = encoding

  // convert to bitArray
  // reorder to match input order before encoding
  // (since these are decoded in little-endian bit order)
  const bits = Array.from(value.toString(2).padStart(totalBits, '0'))
    .map((bit) => parseInt(bit, 10))
    .reverse()

  // first nbits are flags indicating if given layer is present
  // if flag is false, layer is nodata
  const flagBits = bits.slice(0, layers.length)
  const layerBits = bits.slice(layers.length, bits.length)

  let index = 0
  return layers.map(({ id, bits: numLayerBits }, i) => {
    const present = flagBits[i]
    if (!present) {
      index += numLayerBits
      return { id, value: null }
    }

    const layerValue = parseInt(
      layerBits.slice(index, index + numLayerBits).join(''),
      2
    )

    index += numLayerBits

    return {
      id,
      value: layerValue,
    }
  })
}

export const extractPixelData = (map, point, blueprintByColor) => {
  const { lng: longitude, lat: latitude } = point
  const screenPoint = map.project(point)

  const [bndFeature] = map.queryRenderedFeatures(screenPoint, {
    layers: ['bnd'],
  })

  // if no feature is returned, we are outside boundary
  // don't even bother to extract other data
  if (!bndFeature) {
    return null
  }

  const blueprintColor = getPixelValue(map, point, 'blueprint')

  // merge non-null results from all indicatorSources
  const results = []
  indicatorSources.forEach((id) => {
    const layerResults = decodeBits(
      getPixelValue(map, point, id),
      map.getSource(id).encoding
    )

    if (layerResults !== null) {
      // only keep corridors and nonzero indicators
      results.push(
        ...layerResults.filter(
          ({ id: lyrId, value }) =>
            value !== null && (lyrId === 'corridors' || value > 0)
        )
      )
    }
  })

  // console.log('indicator results', results)
  const indicators = arrayToObject(
    results,
    ({ id }) => id,
    ({ value }) => value
  )

  const ecosystems = new Set(
    Object.keys(indicators).map((id) => id.split('_')[0])
  )

  // extract ownership info
  const ownership = {}
  const protection = {}
  const protectedAreas = []
  const ownershipFeatures = map.queryRenderedFeatures(screenPoint, {
    layers: ['ownership'],
  })

  if (ownershipFeatures.length > 0) {
    ownershipFeatures.forEach(
      ({
        properties: {
          FEE_ORGTYP: orgType,
          GAP_STATUS: gapStatus,
          AREA_NAME: areaName,
          FEE_OWNER: owner,
        },
      }) => {
        // hardcode in percent
        ownership[orgType] = 100
        protection[gapStatus] = 100
        protectedAreas.push({ name: areaName, owner })
      }
    )
  }

  const data = {
    type: 'pixel',
    location: { latitude, longitude, zoom: map.getZoom() },
    blueprint: blueprintByColor[blueprintColor] || 0, // default to not a priority
    indicators,
    ecosystems,
    corridors: indicators.corridors === undefined ? null : indicators.corridors,
    ownership,
    protection,
    protectedAreas,
  }

  return data
}
