import React, { useEffect, useRef } from "react"
import PropTypes from "prop-types"
import mapboxgl from "mapbox-gl"
import "mapbox-gl/dist/mapbox-gl.css"
import { Box } from "theme-ui"

import { hasWindow } from "util/dom"
import { getCenterAndZoom } from "./util"
import { config, sources, layers } from "./config"
import { siteMetadata } from "../../../gatsby-config"

const { mapboxToken } = siteMetadata

if (!mapboxToken) {
  console.error(
    "ERROR: Mapbox token is required in gatsby-config.js siteMetadata"
  )
}

// CSS props that control the responsive display of map widgets
const mapWidgetCSS = {
  ".mapboxgl-ctrl-zoom-in, .mapboxgl-ctrl-zoom-out, .mapboxgl-ctrl-compass": {
    display: ["none", "inherit"],
  },
}

const Map = ({}) => {
  // if there is no window, we cannot render this component
  if (!hasWindow) {
    return null
  }

  // this ref holds the map DOM node so that we can pass it into Mapbox GL
  const mapNode = useRef(null)

  // this ref holds the map object once we have instantiated it, so that we
  // can use it in other hooks
  const mapRef = useRef(null)

  useEffect(() => {
    const { bounds, minZoom, maxZoom, styleIDs } = config
    const { center, zoom } = getCenterAndZoom(mapNode.current, bounds, 0.1)

    // Token must be set before constructing map
    mapboxgl.accessToken = mapboxToken

    const map = new mapboxgl.Map({
      container: mapNode.current,
      style: `mapbox://styles/mapbox/${styleIDs[0]}`,
      center,
      zoom,
      minZoom,
      maxZoom,
    })
    mapRef.current = map
    window.map = map // for easier debugging and querying via console

    // TODO: only on desktop
    map.addControl(new mapboxgl.NavigationControl(), "top-right")

    // if (styles.length > 1) {
    //   map.addControl(
    //     new StyleSelector({
    //       styles,
    //       token: mapboxToken,
    //     }),
    //     'bottom-left'
    //   )
    // }

    map.on("load", () => {
      console.log("map onload")
      // add sources
      Object.entries(sources).forEach(([id, source]) => {
        map.addSource(id, source)
      })

      // add layers
      layers.forEach(layer => {
        map.addLayer(layer)
      })
    })

    // hook up map events here, such as click, mouseenter, mouseleave
    // e.g., map.on('click', (e) => {})

    // when this component is destroyed, remove the map
    return () => {
      map.remove()
    }
  }, [])

  return (
    <Box
      sx={{
        width: "100%",
        height: "100%",
        flex: "1 1 auto",
        position: "relative",
        ...mapWidgetCSS,
      }}
    >
      <div ref={mapNode} style={{ width: "100%", height: "100%" }} />
    </Box>
  )
}

Map.propTypes = {}

export default Map
