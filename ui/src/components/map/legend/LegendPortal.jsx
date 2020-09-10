import React from 'react'
import { createPortal } from 'react-dom'

import MobileLegend from './MobileLegend'
import LegendContainer from './LegendContainer'

const LegendPortal = ({ containerRef, isMobile, children }) => {
  console.log('containerRef', containerRef.current)

  if (!containerRef.current) return null

  const container = document.querySelector('.mapboxgl-ctrl-bottom-right')
  const node = document.createElement('div')
  container.appendChild(node)

  const legend = isMobile ? <MobileLegend /> : <LegendContainer />

  return createPortal(legend, node)
}

export default LegendPortal
