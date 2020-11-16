import React, { useEffect, useRef, useState, useCallback, memo } from 'react'
import mapboxgl from 'mapbox-gl'
import 'mapbox-gl/dist/mapbox-gl.css'
import { Box } from 'theme-ui'
import { Crosshairs } from '@emotion-icons/fa-solid'

import { useSearch } from 'components/search'
import { useBreakpoints } from 'components/layout'

import { useBlueprintPriorities, useMapData } from 'components/data'

import { hasWindow } from 'util/dom'
import { useIsEqualEffect } from 'util/hooks'
import { indexBy } from 'util/data'
import { getPixelValue, decodeBits } from './pixels'
import { getCenterAndZoom } from './util'
import { config, sources, layers } from './config'
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

// select sources that have an encoding defined
// there are also layers of the same name
const indicatorSources = Object.entries(sources)
  .filter(([_, { encoding }]) => !!encoding)
  .map(([id, _]) => id)

console.log('indicator sources', indicatorSources)

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
  const mapModeRef = useRef(mapMode)
  const { location } = useSearch()

  const { priorities } = useBlueprintPriorities()
  const blueprintByColor = indexBy(priorities, 'color')

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
      // set default cursor
      map.getCanvas().style.cursor =
        mapModeRef.current === 'pixel' ? 'crosshair' : 'grab'

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

    map.on('click', 'unit-fill', ({ features }) => {
      if (!(features && features.length > 0)) return

      const { properties } = features[0]

      // highlight selected
      map.setFilter('unit-outline-highlight', ['==', 'id', properties.id])

      setMapData(unpackFeatureData(features[0].properties))
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

    // Unhighlight all hover features on mouseout
    map.on('mouseout', () => {
      const { current: prevId } = highlightIDRef
      if (prevId !== null) {
        map.setFeatureState(
          { source: 'mapUnits', sourceLayer: 'units', id: prevId },
          { highlight: false }
        )
      }
    })

    // TODO: Not sure if we want to do this.  OK to zoom in higher but not <10
    // make sure to update pixel values on zoom end in case we get higher resolution
    // data
    // map.on('zoomend', () => {
    //   if (!(isLoaded && mapMode === 'pixel' && mapData !== null)) {
    //     return
    //   }

    //   // if map sources are not done loading, schedule a callback
    //   const dataSources = ['blueprint'].concat(indicatorSources)
    //   const sourcesLoaded = dataSources.filter(
    //     (s) => map.style.sourceCaches[s] && map.style.sourceCaches[s].loaded()
    //   )

    //   const {
    //     location: { latitude: lat, longitude: lng },
    //   } = mapData
    //   if (sourcesLoaded.length < dataSources.length) {
    //     map.getCanvas().style.cursor = 'wait'

    //     map.once('idle', () => {
    //       map.getCanvas().style.cursor = 'crosshair'
    //       extractPixelData({ lng, lat })
    //     })
    //   } else {
    //     extractPixelData({ lng, lat })
    //   }
    // })

    map.on('click', ({ lngLat: point }) => {
      console.log('click', mapModeRef.current, point)

      // TODO: make sure zoom is sufficient
      if (!(isLoaded && mapModeRef.current === 'pixel')) {
        console.log(
          'not loaded or right mode, return',
          isLoaded,
          mapModeRef.current
        )
        return
      }

      if (map.getZoom() < 10) {
        // user clicked but not at right zoom
        console.log('map zoom below thresh', map.getZoom())
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
          extractPixelData(point)
        })
      } else {
        extractPixelData(point)
      }
    })

    // when this component is destroyed, remove the map
    return () => {
      map.remove()
    }
    // intentionally not including mapMode in deps since we update via effects
    // on change
  }, [isMobile, setMapData])

  useEffect(() => {
    mapModeRef.current = mapMode

    if (!isLoaded) return
    const { current: map } = mapRef

    // sometimes map is not fully loaded on hot reload
    if (!map.loaded()) return

    map.getCanvas().style.cursor = mapMode === 'pixel' ? 'crosshair' : 'grab'

    // toggle layer visibility
    if (mapMode === 'pixel') {
      map.setLayoutProperty('unit-fill', 'visibility', 'none')
      map.setLayoutProperty('unit-outline', 'visibility', 'none')

      map.setLayoutProperty('indicators0', 'visibility', 'visible')
      map.setLayoutProperty('indicators1', 'visibility', 'visible')
      map.setLayoutProperty('indicators2', 'visibility', 'visible')
      map.setLayoutProperty('indicators3', 'visibility', 'visible')

      // reset selected outline
      map.setFilter('unit-outline-highlight', ['==', 'id', Infinity])
    } else {
      map.setLayoutProperty('unit-fill', 'visibility', 'visible')
      map.setLayoutProperty('unit-outline', 'visibility', 'visible')

      map.setLayoutProperty('indicators0', 'visibility', 'none')
      map.setLayoutProperty('indicators1', 'visibility', 'none')
      map.setLayoutProperty('indicators2', 'visibility', 'none')
      map.setLayoutProperty('indicators3', 'visibility', 'none')
    }
  }, [isLoaded, mapMode])

  useIsEqualEffect(() => {
    if (!isLoaded) return
    const { current: map } = mapRef

    // sometimes map is not fully loaded on hot reload
    if (!map.loaded()) return

    if (mapData === null) {
      map.setFilter('unit-outline-highlight', ['==', 'id', Infinity])
    }

    if (mapMode === 'pixel') {
      if (mapData === null) {
        if (pixelMarkerRef.current !== null) {
          pixelMarkerRef.current.remove()
          pixelMarkerRef.current = null
        }
      } else {
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
    } else if (locationMarkerRef.current !== null) {
      locationMarkerRef.current.remove()
      locationMarkerRef.current = null
    }
  }, [location, isLoaded])

  const extractPixelData = useCallback(
    (point) => {
      const { current: map } = mapRef
      const { lng: longitude, lat: latitude } = point

      const blueprintValue = getPixelValue(map, point, 'blueprint')

      const blueprint =
        blueprintValue !== null
          ? blueprintByColor[`#${blueprintValue.toString(16)}`]
          : null
      console.log('blueprint', blueprint)

      const results = [
        {
          id: 'blueprint',
          value: blueprintValue,
        },
      ]
      indicatorSources.forEach((id) => {
        const layerResults = decodeBits(
          getPixelValue(map, point, id),
          map.getSource(id).encoding
        )

        // merge in results for this source
        if (layerResults !== null) {
          // filter for non-null layers
          results.push(...layerResults)
        }
      })

      setMapData({
        type: 'pixel',
        location: { latitude, longitude },
        zoom: map.getZoom(),
      })

      console.log('results', results)

      // TODO: call callback to load data
    },
    [blueprintByColor, setMapData]
  )

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
