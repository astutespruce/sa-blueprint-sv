import React, { useEffect, useRef, useState } from "react"
import PropTypes from "prop-types"
import mapboxgl from "mapbox-gl"
import "mapbox-gl/dist/mapbox-gl.css"
import { Box } from "theme-ui"

import { useBreakpoints, useSelectedUnit } from "components/layout"

import { hasWindow } from "util/dom"
import { getCenterAndZoom } from "./util"
import { config, sources, layers } from "./config"
import { unpackFeatureData } from "./features"
import { LegendContainer } from "./legend"
import ZoomInNote from "./ZoomInNote"
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
  ".mapboxgl-ctrl-bottom-left, .mapboxgl-ctrl-bottom-right": {
    bottom: ["3rem", 0],
  },
  "mapboxgl-canvas": {
    outline: "none",
  },
}

const Map = ({ isVisible }) => {
  // if there is no window, we cannot render this component
  if (!hasWindow) {
    return null
  }

  const mapNode = useRef(null)
  const mapRef = useRef(null)
  const mapLoadedRef = useRef(false)
  const highlightIDRef = useRef(null)
  const [zoom, setZoom] = useState(null)

  const breakpoint = useBreakpoints()
  const isMobile = breakpoint === 0
  const { selectedUnit, selectUnit } = useSelectedUnit()

  useEffect(() => {
    const { bounds, maxBounds, minZoom, maxZoom, styleIDs } = config
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
      maxBounds,
    })
    mapRef.current = map
    window.map = map // for easier debugging and querying via console

    if (!isMobile) {
      map.addControl(new mapboxgl.NavigationControl(), "top-right")
    }

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
        map.addLayer(layer, layer.before || null)
      })

      mapLoadedRef.current = true
    })

    map.on("zoomend", () => {
      setZoom(mapRef.current.getZoom())
    })

    map.on("click", "unit-fill", ({ features }) => {
      if (!(features && features.length > 0)) return

      const { id: selectedId, properties } = features[0]
      console.log("selectedID", selectedId, properties.id, properties)

      map.setFilter("unit-outline-highlight", ["==", "id", properties.id])

      selectUnit(unpackFeatureData(features[0].properties))
    })

    // Highlight features under mouse and remove previously highlighted ones
    // TODO: can we do this with just the first feature highlighted and avoid set comparison?
    map.on("mousemove", "unit-fill", ({ features }) => {
      map.getCanvas().style.cursor = "pointer"

      if (!(features && features.length > 0)) return

      const { id } = features[0]

      const { current: prevId } = highlightIDRef
      if (prevId !== null && prevId !== id) {
        map.setFeatureState(
          { source: "mapUnits", sourceLayer: "units", id: prevId },
          { highlight: false }
        )
      }
      map.setFeatureState(
        { source: "mapUnits", sourceLayer: "units", id },
        { highlight: true }
      )
      highlightIDRef.current = id
    })

    // Unhighlight all hover features on mouseout
    map.on("mouseout", () => {
      const { current: prevId } = highlightIDRef
      if (prevId !== null) {
        map.setFeatureState(
          { source: "mapUnits", sourceLayer: "units", id: prevId },
          { highlight: false }
        )
      }
    })

    // when this component is destroyed, remove the map
    return () => {
      map.remove()
    }
  }, [])

  useEffect(() => {
    if (!mapLoadedRef.current) return

    if (selectedUnit === null) {
      map.setFilter("unit-outline-highlight", ["==", "id", Infinity])
    }
  }, [selectedUnit])

  return (
    <Box
      sx={{
        width: "100%",
        height: "100%",
        flex: "1 1 auto",
        position: "relative",
        outline: "none",
        ...mapWidgetCSS,
      }}
    >
      <div ref={mapNode} style={{ width: "100%", height: "100%" }} />

      {isVisible ? (
        <>
          <LegendContainer isMobile={isMobile} />
          <ZoomInNote isVisible={zoom < 8} isMobile={isMobile} />
        </>
      ) : null}
    </Box>
  )
}

Map.propTypes = {
  isVisible: PropTypes.bool,
}

Map.defaultProps = {
  isVisible: true,
}

export default Map
