const EXTENT = 8192 // from mapbox-gl-js/../extent.js

export const getCenterPixel = (map, layerId) => {
  const center = map.getCenter()
  const sourceCache = map.style.sourceCaches[layerId]

  if (!sourceCache) {
    console.error('map source cache not available for', layerId)
    return
  }

  const { transform } = sourceCache

  const tilesIn = sourceCache.tilesIn(
    [map.project(center)],
    transform.maxPitchScaleFactor(),
    false
  )

  if (tilesIn.length === 0) {
    console.debug(`No tiles in ${layerId} available for map center`)
    return
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

  // get scaled tile coordinate for center
  const { x: scaledX, y: scaledY } = tileID.getTilePoint(
    transform.locationCoordinate(center)
  )

  // rescale to tile coords
  const tileX = Math.floor((scaledX / EXTENT) * tileSize)
  const tileY = Math.floor((scaledY / EXTENT) * tileSize)

  if (tileX < 0 || tileY < 0 || tileX > tileSize || tileY > tileSize) {
    console.debug(`Outside bounds of tile ${tileID.toString()}`)
    return
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
}
