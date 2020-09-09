import React, { useEffect, useRef, useState } from "react"
import PropTypes from "prop-types"
import mapboxgl from "mapbox-gl"
import "mapbox-gl/dist/mapbox-gl.css"
import { Box } from "theme-ui"

import { useSearch } from "components/search"
import { useBreakpoints, useSelectedUnit } from "components/layout"

import { hasWindow } from "util/dom"
import { useIsEqualEffect } from "util/hooks"
import { getCenterAndZoom } from "./util"
import { config, sources, layers } from "./config"
import { unpackFeatureData } from "./features"
import { Legend } from "./legend"
import ZoomInNote from "./ZoomInNote"
import StyleToggle from "./StyleToggle"
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
  const locationMarkerRef = useRef(null)
  const [zoom, setZoom] = useState(null)

  const breakpoint = useBreakpoints()
  const isMobile = breakpoint === 0
  const { selectedUnit, selectUnit } = useSelectedUnit()
  const { location } = useSearch()

  useEffect(() => {
    const { bounds, maxBounds, minZoom, maxZoom } = config
    const { center, zoom } = getCenterAndZoom(mapNode.current, bounds, 0.1)

    // Token must be set before constructing map
    mapboxgl.accessToken = mapboxToken

    const map = new mapboxgl.Map({
      container: mapNode.current,
      style: "mapbox://styles/mapbox/light-v9",
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

    map.on("load", () => {
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

      // highlight selected
      map.setFilter("unit-outline-highlight", ["==", "id", properties.id])

      selectUnit(unpackFeatureData(features[0].properties))
    })

    // Highlight units on mouseover
    map.on("mousemove", "unit-fill", ({ features }) => {
      map.getCanvas().style.cursor = "pointer"

      if (!(features && features.length > 0)) {
        return
      }

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

  useIsEqualEffect(() => {
    if (!mapLoadedRef.current) return

    if (selectedUnit === null) {
      map.setFilter("unit-outline-highlight", ["==", "id", Infinity])
    }
  }, [selectedUnit])

  useIsEqualEffect(() => {
    if (!mapLoadedRef.current) return

    if (location !== null) {
      const { current: map } = mapRef
      const { latitude, longitude } = location
      map.flyTo({ center: [longitude, latitude], zoom: 12 })

      if (locationMarkerRef.current === null) {
        locationMarkerRef.current = new mapboxgl.Marker()
          .setLngLat([longitude, latitude])
          .addTo(map)
      } else {
        locationMarkerRef.current.setLngLat([longitude, latitude])
      }
    } else {
      if (locationMarkerRef.current !== null) {
        locationMarkerRef.current.remove()
        locationMarkerRef.current = null
      }
    }
  }, [location])

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
          {!isMobile ? <Legend /> : null}
          <ZoomInNote isVisible={zoom < 8} isMobile={isMobile} />
          <StyleToggle
            mapRef={mapRef}
            sources={sources}
            layers={layers}
            isMobile={isMobile}
          />
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
