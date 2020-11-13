import theme from 'theme'

import { siteMetadata } from '../../../gatsby-config'

const { tileHost } = siteMetadata

export const config = {
  // bounds: [-85.89816168, 28.98417231, -71.28723327, 37.45871183],
  // FIXME
  bounds: [
    // -81.52437938681351,
    // 32.51589056924743,
    // -81.29738295319072,
    // 32.68051488817807,
    -82.32773558,
    32.5711064,
    -82.28111864,
    32.61012435,
  ],

  maxBounds: [-115, 10, -30, 50],
  minZoom: 4,
  maxZoom: 16,
}

export const sources = {
  blueprint: {
    type: 'raster',
    tileSize: 512,
    minzoom: 0,
    maxzoom: 15,
    bounds: [-86.470357, 27.546173, -70.816397, 38.932193],
    tiles: [`${tileHost}/services/sa_blueprint_2020/tiles/{z}/{x}/{y}.png`],
  },
  indicators0: {
    type: 'raster',
    tileSize: 128,
    // FIXME:
    minzoom: 14,
    maxzoom: 16,
    bounds: [-82.327736, 32.571106, -82.281119, 32.610124],
    tiles: [`${tileHost}/services/sa_indicators_0/tiles/{z}/{x}/{y}.png`],
    encoding: {
      bits: 23,
      layers: [
        { id: 'freshwater_imperiledaquaticspecies', bits: 3 },
        { id: 'freshwater_migratoryfishconnectivity', bits: 2 },
        { id: 'freshwater_networkcomplexity', bits: 3 },
        { id: 'freshwater_permeablesurface', bits: 3 },
        { id: 'freshwater_riparianbuffers', bits: 3 },
        { id: 'land_forestbirds', bits: 3 },
      ],
    },
  },
  mapUnits: {
    type: 'vector',
    minzoom: 8,
    maxzoom: 14,
    bounds: [-86.470357, 27.546173, -70.816397, 38.932193],
    tiles: [`${tileHost}/services/sa_map_units/tiles/{z}/{x}/{y}.pbf`],
    // note: can use promoteId: 'id' to promote feature properties ID to feature ID
    promoteId: 'id',
  },
}

// layer in Mapbox Light that we want to come AFTER our layers here
const beforeLayer = 'waterway-label'

export const layers = [
  {
    id: 'indicators0',
    source: 'indicators0',
    type: 'raster',
    minzoom: 0,
    maxzoom: 21,
    paint: {
      'raster-opacity': 0.8,
    },
    before: beforeLayer,
  },

  {
    id: 'blueprint',
    source: 'blueprint',
    type: 'raster',
    minzoom: 0,
    maxzoom: 21,
    // FIXME:
    layout: {
      visibility: 'none',
    },
    paint: {
      'raster-opacity': 0.6,
    },
    before: beforeLayer,
  },
  {
    id: 'unit-fill',
    source: 'mapUnits',
    'source-layer': 'units',
    type: 'fill',

    paint: {
      'fill-color': '#0892D0',
      'fill-opacity': [
        'case',
        ['boolean', ['feature-state', 'highlight'], false],
        0.3,
        0,
      ],
    },
    before: beforeLayer,
  },
  {
    id: 'unit-outline',
    source: 'mapUnits',
    'source-layer': 'units',
    type: 'line',
    paint: {
      'line-opacity': 1,
      'line-color': theme.colors.blue[7],
      'line-width': [
        'interpolate',
        ['linear'],
        ['zoom'],
        8,
        0.25,
        10,
        1,
        13,
        4,
      ],
    },
    before: beforeLayer,
  },
  {
    id: 'unit-outline-highlight',
    source: 'mapUnits',
    'source-layer': 'units',
    type: 'line',
    filter: ['==', 'id', Infinity],
    paint: {
      'line-opacity': 1,
      'line-color': '#000000',
      'line-width': {
        stops: [
          [8, 3],
          [12, 6],
        ],
      },
    },
    before: beforeLayer,
  },
]
