import React, { useEffect, useRef, useState, memo } from 'react'
import mapboxgl from 'mapbox-gl'
import 'mapbox-gl/dist/mapbox-gl.css'
import { Box } from 'theme-ui'
import { Crosshairs } from '@emotion-icons/fa-solid'

import { useSearch } from 'components/search'
import { useBreakpoints, useSelectedUnit } from 'components/layout'

import { useBlueprintPriorities } from 'components/data'

import { hasWindow } from 'util/dom'
import { useIsEqualEffect } from 'util/hooks'
import { indexBy } from 'util/data'
import { getCenterPixel, rgbaToUint, decodeBits } from './pixels'
import { getCenterAndZoom } from './util'
import { config, sources, layers } from './config'
import { unpackFeatureData } from './features'
import { Legend } from './legend'
import ZoomInNote from './ZoomInNote'
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

  const breakpoint = useBreakpoints()
  const isMobile = breakpoint === 0
  const { selectedUnit, selectUnit } = useSelectedUnit()
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

    // FIXME:
    // map.showPadding = true
    map.showTileBoundaries = true

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

    // TODO: only in pixel mode
    // TODO: debounce?
    // TODO: schedule callback if loading tiles
    // TODO: likely also need to do events on moveend
    // map.on('move', () => {
    // const indicatorSources = ['indicators0']
    // const dataSources = ['blueprint'].concat(indicatorSources)

    // const sourcesLoaded = dataSources.filter((s) =>
    //   map.style.sourceCaches[s].loaded()
    // )
    // if (sourcesLoaded.length < dataSources.length) {
    //   return
    // }

    // TODO: update
    // const rgba = getCenterPixel(map, 'blueprint')
    // const value = rgbaToUint(rgba, 'uint32', 65535)
    // console.log('value', value)

    // // to match to hex color:
    // if (value !== null) {
    //   const blueprint = blueprintByColor[`#${value.toString(16)}`]
    //   console.log('blueprint', blueprint)
    // }
    // })

    // this gets called after everything is done
    map.on('moveend', () => {
      map.once('idle', () => {
        const indicatorSources = [
          'indicators0',
          'indicators1',
          'indicators2',
          'indicators3',
        ]
        const results = []
        indicatorSources.forEach((id) => {
          const layerResults = decodeBits(
            getCenterPixel(map, id),
            map.getSource(id).encoding
          )

          console.log(id, ': ', layerResults)

          // merge in results for this source
          if (layerResults !== null) {
            // filter for non-null layers
            results.push(...layerResults)
          }
        })

        console.log('results', results)
      })
    })

    map.on('click', 'unit-fill', ({ features }) => {
      if (!(features && features.length > 0)) return

      const { properties } = features[0]

      // highlight selected
      map.setFilter('unit-outline-highlight', ['==', 'id', properties.id])

      selectUnit(unpackFeatureData(features[0].properties))
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

    // when this component is destroyed, remove the map
    return () => {
      map.remove()
    }
  }, [isMobile, selectUnit])

  useIsEqualEffect(() => {
    if (!isLoaded) return
    const { current: map } = mapRef

    // sometimes map is not fully loaded on hot reload
    if (!map.loaded()) return

    if (selectedUnit === null) {
      map.setFilter('unit-outline-highlight', ['==', 'id', Infinity])
    }
  }, [selectedUnit, isLoaded])

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
      <ZoomInNote map={mapRef.current} isMobile={isMobile} />
      <StyleToggle
        map={mapRef.current}
        sources={sources}
        layers={layers}
        isMobile={isMobile}
      />

      <Crosshairs
        style={{
          position: 'absolute',
          width: '2rem',
          height: '2rem',
          margin: '-1rem 0 0 -1rem',
          left: '50%',
          top: '50%',
        }}
      />
    </Box>
  )
}

// prevent rerender on props change
export default memo(Map, () => true)
