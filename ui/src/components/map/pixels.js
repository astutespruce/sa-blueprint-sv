/* eslint-disable no-bitwise */

const EXTENT = 8192 // from mapbox-gl-js/../extent.js

export const getCenterPixel = (map, layerId) => {
  const center = map.getCenter()
  const sourceCache = map.style.sourceCaches[layerId]

  if (!sourceCache) {
    console.error('map source cache not available for', layerId)
    return null
  }

  const { transform } = sourceCache

  const tilesIn = sourceCache.tilesIn(
    [map.project(center)],
    transform.maxPitchScaleFactor(),
    false
  )

  if (tilesIn.length === 0) {
    console.debug(`No tiles in ${layerId} available for map center`)
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
  const { tileSize } = tile

  if (!(tile.texture && tile.texture.texture)) {
    console.debug(`Tile image not yet loaded ${tileID.toString()}`)
    return null
  }

  // get scaled tile coordinate for center
  const { x: scaledX, y: scaledY } = tileID.getTilePoint(
    transform.locationCoordinate(center)
  )

  // rescale to tile coords
  const tileX = Math.floor((scaledX / EXTENT) * tileSize)
  const tileY = Math.floor((scaledY / EXTENT) * tileSize)

  if (tileX < 0 || tileY < 0 || tileX > tileSize || tileY > tileSize) {
    console.debug(`Outside bounds of tile ${tileID.toString()}`)
    return null
  }

  console.log(
    `Extracting data for tile ${tileID.toString()},  coords: x:${tileX}, y:${tileY}`
  )

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
  console.log(pixels)

  // release framebuffer
  gl.bindFramebuffer(gl.FRAMEBUFFER, null)
  gl.deleteFramebuffer(fb)

  return pixels
}

/**
 * Decode an rgba Uint8ClampedArray to appropriate value for data type, or null if value is nodata
 * @param {string} dtype - data type: uint8, uint16, uint32
 * @param {uint} nodata - nodata value for all layers, typically the highest value for dtype
 * @param {Uint8ClampedArray} rgba - rgba values obtained from image data
 */
export const rgbaToUint = (rgba, dtype = 'uint32', nodata = 65535) => {
  if (rgba === null) {
    return null
  }

  const [r, g, b, a] = rgba

  // if all channels are 0, it is outside tile bounds.
  // if all channels are 255, assume this is NODATA (by convention)
  const sumChannels = r + g + b + a
  if (sumChannels === 0 || sumChannels === 1020) {
    // value is nodata
    return null
  }

  let value = null

  switch (dtype) {
    case 'uint8': {
      value = r
      break
    }
    case 'uint16': {
      value = (r << 16) | (g << 8) | b
      break
    }
    case 'uint32': {
      // the image may be RGB or RGBA
      if (a === 255) {
        // type is RGB
        value = (r << 16) | (g << 8) | b
      } else {
        // Note: browsers do not consistently decode RGBA PNG files to the exact pixel values,
        // which breaks this approach.

        // DO NOT USE RGBA AT THIS TIME!!
        // type is RGBA, use bit shifting to force output to uint
        // TODO: figure out if alpha is first or last value in int
        // value = (((r << 24) >>> 0) | (g << 16) | ((b << 8) + a)) >>> 0;
        // value = (((a << 24) >>> 0) | (r << 16) | ((g << 8) + b)) >>> 0;
        // We can also get the uint32 directly:
        // value = new Uint32Array(rgba.buffer);

        throw new Error('RGBA PNG files are not supported at this time')
      }
      break
    }
    default: {
      console.error('Data type not defined for decoding')
    }
  }

  return value === nodata ? null : value
}

/**
 *
 * @param {object} encoding - encoding parameters: {layers: [{id: <id>, type: <layer type>, values: <unique values (optional)}]}
 * @param {number} value - value to decode
 */
export const exponentialDecoder = (encoding, value) => {
  let internalValue = value
  const values = {}
  const numLayers = encoding.layers.length
  const { base } = encoding
  let decoded = null
  let factor = null
  let remainder = null
  for (let i = numLayers - 1; i >= 0; i -= 1) {
    const layer = encoding.layers[i]
    if (i === 0) {
      decoded = internalValue
    } else {
      factor = base ** i
      remainder = internalValue % factor
      decoded = Math.round((internalValue - remainder) / factor)
      internalValue = remainder
    }

    if (decoded === layer.nodata) {
      values[layer.id] = null
    } else if (layer.type === 'indexed') {
      values[layer.id] = layer.values[decoded]
    } else {
      values[layer.id] = decoded
    }
  }
  return values
}
