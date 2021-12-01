/* eslint-disable no-underscore-dangle */
import React, { useEffect, useRef, useState, useCallback, memo } from 'react'
import mapboxgl from 'mapbox-gl'
import 'mapbox-gl/dist/mapbox-gl.css'
import { Box } from 'theme-ui'
import { Crosshairs } from '@emotion-icons/fa-solid'

import { useSearch } from 'components/search'
import { useBreakpoints } from 'components/layout'

import { useBlueprintPriorities, useMapData } from 'components/data'

import { hasWindow, isLocalDev } from 'util/dom'
import { useIsEqualEffect } from 'util/hooks'
import { extractPixelData } from './pixels'
import { getCenterAndZoom } from './util'
import {
  mapConfig as config,
  sources,
  indicatorSources,
  layers,
} from './mapConfig'
import { unpackFeatureData } from './features'
import { Legend } from './legend'
import MapModeToggle from './MapModeToggle'
import StyleToggle from './StyleToggle'
import { siteMetadata } from '../../../gatsby-config'

const { mapboxToken } = siteMetadata

if (!mapboxToken) {
  // eslint-disable-next-line no-console
  console.error(
    'ERROR: Mapbox token is required in gatsby-config.js siteMetadata'
  )
}

// CSS props that control the responsive display of map widgets
const mapWidgetCSS = {
  '.mapboxgl-ctrl-zoom-in, .mapboxgl-ctrl-zoom-out, .mapboxgl-ctrl-compass': {
    display: ['none', 'inherit'],
  },
  '.mapboxgl-canvas': {
    outline: 'none',
  },
}

const Map = () => {
  const mapNode = useRef(null)
  const mapRef = useRef(null)
  const [isLoaded, setIsLoaded] = useState(false)
  const [isBlueprintVisible, setIsBlueprintVisible] = useState(true)
  const highlightIDRef = useRef(null)
  const locationMarkerRef = useRef(null)

  const breakpoint = useBreakpoints()
  const isMobile = breakpoint === 0
  const { data: mapData, mapMode, setData: setMapData } = useMapData()
  const { colorIndex: blueprintByColor } = useBlueprintPriorities()
  const mapModeRef = useRef(mapMode)
  const { location } = useSearch()

  useEffect(() => {
    // if there is no window, we cannot render this component
    if (!hasWindow) {
      return undefined
    }

    const { bounds, maxBounds, minZoom, maxZoom } = config
    const { center, zoom } = getCenterAndZoom(mapNode.current, bounds, 0.1)

    // Token must be set before constructing map
    mapboxgl.accessToken = mapboxToken

    const map = new mapboxgl.Map({
      container: mapNode.current,
      style: 'mapbox://styles/mapbox/light-v9',
      center,
      zoom,
      minZoom,
      maxZoom,
      maxBounds,
    })

    mapRef.current = map
    window.map = map // for easier debugging and querying via console

    if (!isMobile) {
      map.addControl(new mapboxgl.NavigationControl(), 'top-right')
    }

    map.on('load', () => {
      // due to styling components loading at different types, the containing
      // nodes don't always have height set; force larger view
      if (isLocalDev) {
        map.resize()
        const { zoom: curZoom } = getCenterAndZoom(mapNode.current, bounds, 0.1)
        map.setZoom(curZoom)
      }

      // add sources
      Object.entries(sources).forEach(([id, source]) => {
        map.addSource(id, source)
      })

      // add layers
      layers.forEach((layer) => {
        map.addLayer(layer, layer.before || null)
      })

      // update state once to trigger other components to update with map object
      setIsLoaded(() => true)
    })

    // Highlight units on mouseover
    map.on('mousemove', 'unit-fill', ({ features }) => {
      if (!map.isStyleLoaded()) {
        return
      }

      map.getCanvas().style.cursor = 'pointer'

      if (!(features && features.length > 0)) {
        return
      }

      const { id } = features[0]

      const { current: prevId } = highlightIDRef
      if (prevId !== null && prevId !== id) {
        map.setFeatureState(
          { source: 'mapUnits', sourceLayer: 'units', id: prevId },
          { highlight: false }
        )
      }
      map.setFeatureState(
        { source: 'mapUnits', sourceLayer: 'units', id },
        { highlight: true }
      )
      highlightIDRef.current = id
    })

    map.on('mouseout', 'unit-fill', () => {
      if (!map.isStyleLoaded()) {
        return
      }

      const { current: prevId } = highlightIDRef
      if (prevId !== null) {
        map.setFeatureState(
          { source: 'mapUnits', sourceLayer: 'units', id: prevId },
          { highlight: false }
        )
      }
    })

    // Unhighlight all hover features on mouseout of map
    map.on('mouseout', () => {
      const { current: prevId } = highlightIDRef
      if (prevId !== null) {
        map.setFeatureState(
          { source: 'mapUnits', sourceLayer: 'units', id: prevId },
          { highlight: false }
        )
      }
    })

    map.on('click', ({ lngLat: point }) => {
      if (mapModeRef.current === 'pixel') return

      // if (mapModeRef.current !== 'pixel') {
      const features = map.queryRenderedFeatures(map.project(point), {
        layers: ['unit-fill'],
      })

      if (!(features && features.length > 0)) {
        setMapData(null)
        return
      }

      const { properties } = features[0]

      // highlight selected
      map.setFilter('unit-outline-highlight', ['==', 'id', properties.id])

      setMapData(unpackFeatureData(features[0].properties))
    })

    map.on('move', () => {
      if (mapModeRef.current === 'pixel') {
        getPixelData()
      }
    })

    map.on('zoomend', () => {
      if (mapModeRef.current === 'pixel') {
        getPixelData()
      }
    })

    // when this component is destroyed, remove the map
    return () => {
      // remove markers

      removeLocationMarker()
      map.remove()
    }
    // intentionally not including mapMode in deps since we update via effects
    // on change
  }, [isMobile, setMapData, getPixelData])

  useEffect(() => {
    mapModeRef.current = mapMode

    if (!isLoaded) return
    const { current: map } = mapRef

    // toggle layer visibility
    if (mapMode === 'pixel') {
      if (map.getZoom() >= 7) {
        map.once('idle', getPixelData)
      }

      map.setLayoutProperty('unit-fill', 'visibility', 'none')
      map.setLayoutProperty('unit-outline', 'visibility', 'none')

      map.setLayoutProperty('indicators0', 'visibility', 'visible')
      map.setLayoutProperty('indicators1', 'visibility', 'visible')
      map.setLayoutProperty('indicators2', 'visibility', 'visible')
      map.setLayoutProperty('indicators3', 'visibility', 'visible')
      map.setLayoutProperty('indicators4', 'visibility', 'visible')
      map.setLayoutProperty('ownership', 'visibility', 'visible')

      // reset selected outline
      map.setFilter('unit-outline-highlight', ['==', 'id', Infinity])
    } else {
      map.setLayoutProperty('unit-fill', 'visibility', 'visible')
      map.setLayoutProperty('unit-outline', 'visibility', 'visible')

      map.setLayoutProperty('indicators0', 'visibility', 'none')
      map.setLayoutProperty('indicators1', 'visibility', 'none')
      map.setLayoutProperty('indicators2', 'visibility', 'none')
      map.setLayoutProperty('indicators3', 'visibility', 'none')
      map.setLayoutProperty('indicators4', 'visibility', 'none')
      map.setLayoutProperty('ownership', 'visibility', 'none')
    }
  }, [isLoaded, mapMode, getPixelData])

  useIsEqualEffect(() => {
    if (!isLoaded) return
    const { current: map } = mapRef

    // sometimes map is not fully loaded on hot reload
    if (!map.loaded()) return

    if (mapData === null) {
      map.setFilter('unit-outline-highlight', ['==', 'id', Infinity])
    }
  }, [mapData, isLoaded])

  useIsEqualEffect(() => {
    if (!isLoaded) return

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
      removeLocationMarker()
    }
  }, [location, isLoaded])

  const getPixelData = useCallback(() => {
    // if (mapModeRef.current !== 'pixel') return

    const { current: map } = mapRef
    if (!map) return

    if (map.getZoom() < 7) {
      setMapData(null)
      return
    }

    const dataSources = ['blueprint'].concat(indicatorSources)
    // Note: these are at map.style._otherSourceCaches for mapbox-gl-js >= 2.0
    const sourcesLoaded = dataSources.filter(
      (s) =>
        map.style._otherSourceCaches[s] &&
        map.style._otherSourceCaches[s].loaded()
    )
    if (sourcesLoaded.length < dataSources.length) {
      // if map sources are not done loading, schedule a callback
      // map.once('idle', getPixelData)
      map.once('idle', () => {
        setMapData(extractPixelData(map, map.getCenter(), blueprintByColor))
      })
      // set loading and pass coordinates for header to avoid jitter
      const { lng: longitude, lat: latitude } = map.getCenter()
      setMapData({
        type: 'pixel',
        isLoading: true,
        location: {
          longitude,
          latitude,
        },
      })
    } else {
      // NOTE: if outside bounds, this will be null and unselect data
      setMapData(extractPixelData(map, map.getCenter(), blueprintByColor))
    }
  }, [blueprintByColor, setMapData]) // setMapDataLoading

  const handleToggleBlueprintVisibile = useCallback(() => {
    const { current: map } = mapRef
    if (!map) return

    setIsBlueprintVisible((prevVisible) => {
      const newIsVisible = !prevVisible
      if (newIsVisible) {
        map.setPaintProperty('blueprint', 'raster-opacity', 0.6)
      } else {
        map.setPaintProperty('blueprint', 'raster-opacity', 0)
      }
      return newIsVisible
    })
  }, [])

  const removeLocationMarker = () => {
    if (locationMarkerRef.current !== null) {
      locationMarkerRef.current.remove()
      locationMarkerRef.current = null
    }
  }

  // if there is no window, we cannot render this component
  if (!hasWindow) {
    return null
  }

  return (
    <Box
      sx={{
        width: '100%',
        height: '100%',
        flex: '1 1 auto',
        position: 'relative',
        outline: 'none',
        ...mapWidgetCSS,
      }}
    >
      <div ref={mapNode} style={{ width: '100%', height: '100%' }} />

      {mapMode === 'pixel' &&
      mapRef.current &&
      mapRef.current.getZoom() >= 7 ? (
        <Box
          sx={{
            position: 'absolute',
            left: '50%',
            top: '50%',
            ml: '-1rem',
            mt: '-1rem',
            pointerEvents: 'none',
            opacity: 0.75,
          }}
        >
          <Crosshairs size="2rem" />
        </Box>
      ) : null}

      {!isMobile ? (
        <Legend
          isVisible={isBlueprintVisible}
          onToggleVisibility={handleToggleBlueprintVisibile}
        />
      ) : null}

      <MapModeToggle map={mapRef.current} isMobile={isMobile} />

      <StyleToggle
        map={mapRef.current}
        sources={sources}
        layers={layers}
        mapMode={mapMode}
        isMobile={isMobile}
      />
    </Box>
  )
}

// prevent rerender on props change
export default memo(Map, () => true)
