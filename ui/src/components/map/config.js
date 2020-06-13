import theme from "theme"

import { siteMetadata } from "../../../gatsby-config"

const { tileHost } = siteMetadata

export const config = {
  bounds: [-85.89816168, 28.98417231, -71.28723327, 37.45871183],
  // FIXME: temp:
  // bounds: [-81.392, 31.5566, -80.3124, 32.509],
  maxBounds: [-92, 10, -62, 50],
  styleIDs: ["light-v9", "satellite-streets-v10"],
  minZoom: 4,
  maxZoom: 24,
}

export const sources = {
  blueprint: {
    type: "raster",
    tileSize: 256, // TODO: 512
    minzoom: 4,
    maxZoom: 15,
    bounds: [-86.470357, 27.546173, -70.816397, 38.932193],
    tiles: [`${tileHost}/services/blueprint2_2/tiles/{z}/{x}/{y}.png`],
  },
  sa: {
    type: "vector",
    minzoom: 8,
    maxzoom: 14,
    bounds: [-86.470357, 27.546173, -70.816397, 38.932193],
    tiles: [`${tileHost}/services/units_atts/tiles/{z}/{x}/{y}.pbf`],
    // note: can use promoteId: 'id' to promote feature properties ID to feature ID
    promoteId: "id",
  },
}

// layer in Mapbox Light that we want to come AFTER our layers here
const beforeLayer = "waterway-label"

export const layers = [
  {
    id: "blueprint",
    source: "blueprint",
    type: "raster",
    paint: {
      "raster-opacity": {
        stops: [
          [4, 0.4],
          [10, 0.4],
          [12, 0.25],
        ],
      },
    },
    before: beforeLayer,
  },
  {
    id: "unit-fill",
    source: "sa",
    "source-layer": "units",
    type: "fill",

    paint: {
      "fill-color": "#0892D0",
      "fill-opacity": [
        "case",
        ["boolean", ["feature-state", "highlight"], false],
        0.3,
        0,
      ],
    },
    before: beforeLayer,
  },
  {
    id: "unit-outline",
    source: "sa",
    "source-layer": "units",
    type: "line",
    paint: {
      "line-opacity": 1,
      "line-color": theme.colors.blue[7],
      "line-width": [
        "interpolate",
        ["linear"],
        ["zoom"],
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
    id: "unit-outline-highlight",
    source: "sa",
    "source-layer": "units",
    type: "line",
    filter: ["==", "id", Infinity],
    paint: {
      "line-opacity": 1,
      "line-color": "#000000",
      "line-width": {
        stops: [
          [8, 3],
          [12, 6],
        ],
      },
    },
    before: beforeLayer,
  },
]
