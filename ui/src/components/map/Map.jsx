import React, { useEffect, useRef, useState, useCallback, memo } from 'react'
import mapboxgl from 'mapbox-gl'
import 'mapbox-gl/dist/mapbox-gl.css'
import { Box } from 'theme-ui'

import { useSearch } from 'components/search'
import { useBreakpoints } from 'components/layout'

import { useBlueprintPriorities, useMapData } from 'components/data'

import { hasWindow } from 'util/dom'
import { useIsEqualEffect } from 'util/hooks'
import { extractPixelData, getPixelValue } from './pixels'
import { getCenterAndZoom } from './util'
import { config, sources, indicatorSources, layers } from './config'
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
  const highlightIDRef = useRef(null)
  const locationMarkerRef = useRef(null)
  const pixelMarkerRef = useRef(null)

  const breakpoint = useBreakpoints()
  const isMobile = breakpoint === 0
  const { data: mapData, mapMode, setData: setMapData } = useMapData()
  const { colorIndex: blueprintByColor } = useBlueprintPriorities()
  const mapModeRef = useRef(mapMode)
  const { location } = useSearch()

  useEffect(() => {
    // if there is no window, we cannot render this component
    if (!hasWindow) {
      return null
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
      if (mapModeRef.current !== 'pixel') {
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

        return
      }

      if (map.getZoom() < 7) {
        // user clicked but not at right zoom
        setMapData(null)
        return
      }

      // if map sources are not done loading, schedule a callback
      const dataSources = ['blueprint'].concat(indicatorSources)
      const sourcesLoaded = dataSources.filter(
        (s) => map.style.sourceCaches[s] && map.style.sourceCaches[s].loaded()
      )
      if (sourcesLoaded.length < dataSources.length) {
        map.getCanvas().style.cursor = 'wait'

        map.once('idle', () => {
          map.getCanvas().style.cursor = 'crosshair'
          getPixelData(point)
        })
      } else {
        getPixelData(point)
      }
    })

    map.on('zoomend', () => {
      if (mapModeRef.current === 'pixel' && map.getZoom() >= 7) {
        map.getCanvas().style.cursor = 'crosshair'
      } else {
        map.getCanvas().style.cursor = 'grab'
      }
    })

    // when this component is destroyed, remove the map
    return () => {
      // remove markers

      removeLocationMarker()
      removePixelMarker()

      map.remove()
    }
    // intentionally not including mapMode in deps since we update via effects
    // on change
  }, [isMobile, setMapData, getPixelData])

  useEffect(() => {
    mapModeRef.current = mapMode

    if (!isLoaded) return
    const { current: map } = mapRef

    map.getCanvas().style.cursor =
      mapMode === 'pixel' && map.getZoom() >= 7 ? 'crosshair' : 'grab'

    // toggle layer visibility
    if (mapMode === 'pixel') {
      map.setLayoutProperty('unit-fill', 'visibility', 'none')
      map.setLayoutProperty('unit-outline', 'visibility', 'none')

      map.setLayoutProperty('indicators0', 'visibility', 'visible')
      map.setLayoutProperty('indicators1', 'visibility', 'visible')
      map.setLayoutProperty('indicators2', 'visibility', 'visible')
      map.setLayoutProperty('indicators3', 'visibility', 'visible')
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
      map.setLayoutProperty('ownership', 'visibility', 'none')

      removePixelMarker()
    }
  }, [isLoaded, mapMode])

  useIsEqualEffect(() => {
    if (!isLoaded) return
    const { current: map } = mapRef

    // sometimes map is not fully loaded on hot reload
    if (!map.loaded()) return

    if (mapData === null) {
      map.setFilter('unit-outline-highlight', ['==', 'id', Infinity])

      removePixelMarker()
    }

    if (mapMode === 'pixel') {
      if (mapData !== null) {
        const {
          location: { latitude, longitude },
        } = mapData
        if (pixelMarkerRef.current === null) {
          pixelMarkerRef.current = new mapboxgl.Marker({
            color: '#000',
          })
            .setLngLat([longitude, latitude])
            .addTo(map)
        } else {
          pixelMarkerRef.current.setLngLat([longitude, latitude])
        }
      }
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

  const getPixelData = useCallback(
    (point) => {
      const { current: map } = mapRef
      const pixelData = extractPixelData(map, point, blueprintByColor)

      // NOTE: if outside bounds, this will be null and unselect data
      setMapData(pixelData)
    },
    [blueprintByColor, setMapData]
  )

  const removeLocationMarker = () => {
    if (locationMarkerRef.current !== null) {
      locationMarkerRef.current.remove()
      locationMarkerRef.current = null
    }
  }

  const removePixelMarker = () => {
    if (pixelMarkerRef.current !== null) {
      pixelMarkerRef.current.remove()
      pixelMarkerRef.current = null
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

      {!isMobile ? <Legend /> : null}

      <MapModeToggle map={mapRef.current} isMobile={isMobile} />

      <StyleToggle
        map={mapRef.current}
        sources={sources}
        layers={layers}
        isMobile={isMobile}
      />
    </Box>
  )
}

// prevent rerender on props change
export default memo(Map, () => true)
