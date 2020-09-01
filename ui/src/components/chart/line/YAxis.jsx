import React from "react"
import PropTypes from "prop-types"

import { formatNumber } from "util/format"

const YAxis = ({ ticks, stroke, strokeWidth, fontSize, labelColor }) => {
  return (
    <g>
      <line
        x1={0}
        y1={ticks[0].y}
        x2={0}
        y2={ticks[ticks.length - 1].y}
        stroke={stroke}
        strokeWidth={strokeWidth}
      />
      {ticks.map(({ y, label }) => (
        <g key={y} transform={`translate(-4, ${y})`}>
          <line x1={0} y1={0} x2={8} y2={0} stroke={stroke} strokeWidth={1} />

          <text textAnchor="end" x={-4} y={fontSize / 2} fill={labelColor}>
            {label}
          </text>
        </g>
      ))}
    </g>
  )
}

YAxis.propTypes = {
  ticks: PropTypes.arrayOf(
    PropTypes.shape({
      y: PropTypes.number.isRequired,
      label: PropTypes.string,
    })
  ).isRequired,
  stroke: PropTypes.string,
  strokeWidth: PropTypes.number,
  fontSize: PropTypes.number,
}

YAxis.defaultProps = {
  strokeWidth: 1,
  stroke: "#AAA",
  fontSize: 10,
  labelColor: "#666",
}

export default YAxis
