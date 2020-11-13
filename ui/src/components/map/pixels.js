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

  // release framebuffer
  gl.bindFramebuffer(gl.FRAMEBUFFER, null)
  gl.deleteFramebuffer(fb)

  // pixels are decoded as b,g,r values because of how we encode them

  // decode to uint
  const [b, g, r] = pixels
  const value = (r << 16) | (g << 8) | b
  console.log('pixels', pixels, '==>', value)

  return value
}

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

    console.log(
      id,
      layerBits.slice(index, index + numLayerBits).join(''),
      '==>',
      layerValue
    )

    index += numLayerBits

    return {
      id,
      value: layerValue,
    }
  })
}

// Not used:

// /**
//  * Decode an rgba Uint8ClampedArray to appropriate value for data type, or null if value is nodata
//  * @param {string} dtype - data type: uint8, uint16, uint32
//  * @param {uint} nodata - nodata value for all layers, typically the highest value for dtype
//  * @param {Uint8ClampedArray} rgba - rgba values obtained from image data
//  */
// export const rgbaToUint = (rgb, dtype = 'uint32', nodata = 65535) => {
//   if (rgba === null) {
//     return null
//   }

//   const [r, g, b, a] = rgba

//   // if all channels are 0, it is outside tile bounds.
//   // if all channels are 255, assume this is NODATA (by convention)
//   const sumChannels = r + g + b + a
//   if (sumChannels === 0 || sumChannels === 1020) {
//     // value is nodata
//     return null
//   }

//   let value = null

//   switch (dtype) {
//     case 'uint8': {
//       value = r
//       break
//     }
//     case 'uint16': {
//       value = (r << 16) | (g << 8) | b
//       break
//     }
//     case 'uint32': {
//       // the image may be RGB or RGBA
//       if (a === 255) {
//         // type is RGB
//         value = (r << 16) | (g << 8) | b
//       } else {
//         // Note: browsers do not consistently decode RGBA PNG files to the exact pixel values,
//         // which breaks this approach.

//         // DO NOT USE RGBA AT THIS TIME!!
//         // type is RGBA, use bit shifting to force output to uint
//         // TODO: figure out if alpha is first or last value in int
//         // value = (((r << 24) >>> 0) | (g << 16) | ((b << 8) + a)) >>> 0;
//         // We can also get the uint32 directly:
//         // value = new Uint32Array(rgba.buffer);

//         throw new Error('RGBA PNG files are not supported at this time')
//       }
//       break
//     }
//     default: {
//       console.error('Data type not defined for decoding')
//     }
//   }

//   return value === nodata ? null : value
// }
