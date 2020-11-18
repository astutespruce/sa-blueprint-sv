/* eslint-disable no-bitwise */

import { arrayToObject } from 'util/data'
import { indicatorSources } from './config'

const EXTENT = 8192 // from mapbox-gl-js/../extent.js

/**
 * Extracts RGB data from a pixel at a location, encoded as a uint32 value.
 * Returns null if data is not yet loaded or point is outside bounds for
 * available tiles.
 * @param {Object} map - mapbox GL map object
 * @param {Object} point - {lat, lng} of point for which to extract pixel data
 * @param {String} layerId - layer from which to extract pixel data
 */
export const getPixelValue = (map, point, layerId) => {
  const sourceCache = map.style.sourceCaches[layerId]

  if (!sourceCache) {
    console.error('map source cache not available for', layerId)
    return null
  }

  const { transform } = sourceCache

  const tilesIn = sourceCache.tilesIn(
    [map.project(point)],
    transform.maxPitchScaleFactor(),
    false
  )

  if (tilesIn.length === 0) {
    // console.debug(`No tiles in ${layerId} available for point`)
    return null
  }

  // sort tiles
  // from mapbox-gl-js/.../query_features.js
  tilesIn.sort(
    ({ tileID: idA }, { tileID: idB }) =>
      idA.overscaledZ - idB.overscaledZ ||
      idA.canonical.y - idB.canonical.y ||
      idA.wrap - idB.wrap ||
      idA.canonical.x - idB.canonical.x
  )

  const [{ tile, tileID }] = tilesIn // only need the first, this is highest zoom

  if (!(tile.texture && tile.texture.size)) {
    // not fully loaded yet
    return null
  }

  // NOTE: raw tiles may be smaller images than they claim to be in the
  // layer tileSize property (they are overzoomed)
  const tileSize = tile.texture.size[0]

  if (!(tile.texture && tile.texture.texture)) {
    // console.debug(`Tile image not yet loaded ${tileID.toString()}`)
    return null
  }

  // get scaled tile coordinate for point
  const { x: scaledX, y: scaledY } = tileID.getTilePoint(
    transform.locationCoordinate(point)
  )

  // rescale to tile coords
  const tileX = Math.floor((scaledX / EXTENT) * tileSize)
  const tileY = Math.floor((scaledY / EXTENT) * tileSize)

  if (tileX < 0 || tileY < 0 || tileX > tileSize || tileY > tileSize) {
    // console.debug(`Outside bounds of tile ${tileID.toString()}`)
    return null
  }

  // console.debug(
  //   `Extracting data for tile ${tileID.toString()},  coords: x:${tileX}, y:${tileY}`
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
  // console.log('pixels', pixels, '==>', value)

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

  const [bndFeature] = map.queryRenderedFeatures(map.project(point), {
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
      results.push(...layerResults.filter(({ value }) => value !== null))
    }
  })

  console.log('indicator results', results)
  const indicators = arrayToObject(
    results,
    ({ id }) => id,
    ({ value }) => value
  )

  const data = {
    type: 'pixel',
    location: { latitude, longitude, zoom: map.getZoom() },
    blueprint: blueprintByColor[blueprintColor] || 0, // default to not a priority
    indicators: Object.keys(indicators),
    ...indicators,
    corridors: indicators.corridors === undefined ? null : indicators.corridors,
  }

  console.log('data', data)

  return data
}
