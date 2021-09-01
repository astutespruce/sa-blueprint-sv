import theme from 'theme'

import { siteMetadata } from '../../../gatsby-config'

const { tileHost } = siteMetadata

export const config = {
  bounds: [-85.89816168, 28.98417231, -71.28723327, 37.45871183],
  // FIXME
  // bounds: [
  //   // test area 1
  //   // -81.52437938681351,
  //   // 32.51589056924743,
  //   // -81.29738295319072,
  //   // 32.68051488817807,
  //   // test area 2
  // -77.28581582039118,
  // 37.21040906844688,
  // -77.22931903990204,
  // 37.2548924014517,
  // test area 3
  //   -76.93915117797323,
  //   37.012453160576655,
  //   -76.91005681150797,
  //   37.03819853841662,
  // ],

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
    tiles: [`${tileHost}/services/sa_blueprint_2021/tiles/{z}/{x}/{y}.png`],
  },
  // Note: encoding order was stored incorrectly during previous encoding
  // it was fixed manually here
  indicators0: {
    type: 'raster',
    tileSize: 512, // NOTE: actual tiles are 128, but this overzooms them
    minzoom: 7,
    maxzoom: 14,
    bounds: [-87.234705, 28.173085, -75.063588, 38.300913],
    tiles: [`${tileHost}/services/sa_indicators_0/tiles/{z}/{x}/{y}.png`],
    encoding: {
      bits: 21,
      layers: [
        { id: 'freshwater_imperiledaquaticspecies', bits: 3 },
        { id: 'freshwater_atlanticmigratoryfishhabitat', bits: 4 },
        { id: 'freshwater_networkcomplexity', bits: 3 },
        { id: 'freshwater_permeablesurface', bits: 3 },
        { id: 'freshwater_riparianbuffers', bits: 3 },
      ],
    },
  },
  indicators1: {
    type: 'raster',
    tileSize: 512,
    minzoom: 7,
    maxzoom: 14,
    bounds: [-85.388054, 27.417995, -70.808243, 38.823931],
    tiles: [`${tileHost}/services/sa_indicators_1/tiles/{z}/{x}/{y}.png`],
    encoding: {
      bits: 24,
      layers: [
        { id: 'land_maritimeforestextent', bits: 2 },
        { id: 'land_shorelinecondition', bits: 3 },
        { id: 'marine_estuarinecondition', bits: 3 },
        { id: 'marine_fishhabitat', bits: 4 },
        { id: 'marine_mammals', bits: 3 },
        { id: 'marine_hardbottomcoral', bits: 3 },
      ],
    },
  },
  indicators2: {
    type: 'raster',
    tileSize: 512,
    minzoom: 7,
    maxzoom: 14,
    bounds: [-87.23906, 27.419516, -70.816102, 39.009566],
    tiles: [`${tileHost}/services/sa_indicators_2/tiles/{z}/{x}/{y}.png`],
    encoding: {
      bits: 23,
      layers: [
        { id: 'freshwater_gulfmigratoryfishhabitat', bits: 2 },
        { id: 'land_equitableparkaccess', bits: 3 },
        { id: 'land_forestedwetlandextent', bits: 2 },
        { id: 'land_greenways', bits: 3 },
        { id: 'land_intactcores', bits: 2 },
        { id: 'land_lowurbanhistoric', bits: 2 },
        { id: 'land_pinebirds', bits: 2 },
      ],
    },
  },
  indicators3: {
    type: 'raster',
    tileSize: 512,
    minzoom: 7,
    maxzoom: 14,
    bounds: [-87.23906, 27.417868, -70.807588, 39.009566],
    tiles: [`${tileHost}/services/sa_indicators_3/tiles/{z}/{x}/{y}.png`],
    encoding: {
      bits: 24,
      layers: [
        { id: 'land_amphibianreptiles', bits: 2 },
        { id: 'land_marshextent', bits: 2 },
        { id: 'land_marshbirds', bits: 2 },
        { id: 'land_piedmontprairie', bits: 3 },
        { id: 'land_resilientsites', bits: 3 },
        { id: 'land_urbanparksize', bits: 3 },
        { id: 'corridors', bits: 2 },
      ],
    },
  },
  indicators4: {
    type: 'raster',
    tileSize: 512,
    minzoom: 7,
    maxzoom: 14,
    bounds: [-87.23906, 27.417868, -70.807588, 39.009566],
    tiles: [`${tileHost}/services/sa_indicators_4/tiles/{z}/{x}/{y}.png`],
    encoding: {
      bits: 16,
      layers: [
        { id: 'land_beachbirds', bits: 3 },
        { id: 'land_firefrequency', bits: 3 },
        { id: 'land_forestbirds', bits: 3 },
        { id: 'marine_birds', bits: 3 },
      ],
    },
  },
  mapUnits: {
    type: 'vector',
    minzoom: 4,
    maxzoom: 14,
    bounds: [-86.470357, 27.546173, -70.816397, 38.932193],
    tiles: [`${tileHost}/services/sa_map_units/tiles/{z}/{x}/{y}.pbf`],
    // note: can use promoteId: 'id' to promote feature properties ID to feature ID
    promoteId: 'id',
  },
  ownership: {
    type: 'vector',
    minzoom: 7,
    maxzoom: 15,
    bounds: [-86.470357, 27.546173, -70.816397, 38.932193],
    tiles: [`${tileHost}/services/sa_ownership/tiles/{z}/{x}/{y}.pbf`],
  },
}

// select sources that have an encoding defined
// there are also layers of the same name
export const indicatorSources = Object.entries(sources)
  .filter(([_, { encoding }]) => !!encoding)
  .map(([id, _]) => id)

// layer in Mapbox Light that we want to come AFTER our layers here
const beforeLayer = 'waterway-label'

export const layers = [
  {
    id: 'ownership',
    source: 'ownership',
    'source-layer': 'ownership',
    type: 'fill',
    paint: {
      'fill-color': '#FFF',
      'fill-opacity': 0,
    },
    before: beforeLayer,
  },
  {
    id: 'indicators0',
    source: 'indicators0',
    type: 'raster',
    minzoom: 0,
    maxzoom: 21,
    paint: {
      'raster-opacity': 0,
    },
    before: beforeLayer,
  },
  {
    id: 'indicators1',
    source: 'indicators1',
    type: 'raster',
    minzoom: 0,
    maxzoom: 21,
    paint: {
      'raster-opacity': 0,
    },
    before: beforeLayer,
  },
  {
    id: 'indicators2',
    source: 'indicators2',
    type: 'raster',
    minzoom: 0,
    maxzoom: 21,
    paint: {
      'raster-opacity': 0,
    },
    before: beforeLayer,
  },
  {
    id: 'indicators3',
    source: 'indicators3',
    type: 'raster',
    minzoom: 0,
    maxzoom: 21,
    paint: {
      'raster-opacity': 0,
    },
    before: beforeLayer,
  },
  {
    id: 'indicators4',
    source: 'indicators4',
    type: 'raster',
    minzoom: 0,
    maxzoom: 21,
    paint: {
      'raster-opacity': 0,
    },
    before: beforeLayer,
  },
  {
    id: 'blueprint',
    source: 'blueprint',
    type: 'raster',
    minzoom: 0,
    maxzoom: 21,
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
    layout: {
      visibility: 'none',
    },
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
    layout: {
      visibility: 'none',
    },
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
  // render boundary to capture clicks and determine if pixel is in our outside bounds
  {
    id: 'bnd',
    source: 'mapUnits',
    'source-layer': 'boundary',
    type: 'fill',
    paint: {
      'fill-opacity': 0,
      'fill-color': '#FFFFFF',
    },
  },
  {
    id: 'bnd-outline',
    source: 'mapUnits',
    'source-layer': 'boundary',
    type: 'line',
    paint: {
      'line-color': '#000000',
      'line-width': {
        stops: [
          [4, 0.1],
          [8, 1],
        ],
      },
      'line-opacity': {
        stops: [
          [8, 1],
          [12, 0.2],
          [14, 0.1],
          [15, 0],
        ],
      },
    },
  },
]
