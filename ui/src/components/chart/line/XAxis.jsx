import React from "react"
import PropTypes from "prop-types"

const XAxis = ({ ticks, stroke, strokeWidth, fontSize, labelColor }) => {
  return (
    <g>
      <line
        y1={0}
        x1={ticks[0].x}
        y2={0}
        x2={ticks[ticks.length - 1].x}
        stroke={stroke}
        strokeWidth={strokeWidth}
      />

      {ticks.map(({ x, label }) => (
        <g key={x} transform={`translate(${x}, -4)`}>
          <line x1={0} y1={0} x2={0} y2={8} stroke={stroke} strokeWidth={1} />

          <text textAnchor="middle" x={0} y={fontSize + 12} fill={labelColor}>
            {label}
          </text>
        </g>
      ))}
    </g>
  )
}

XAxis.propTypes = {
  ticks: PropTypes.arrayOf(
    PropTypes.shape({
      x: PropTypes.number.isRequired,
      label: PropTypes.string,
    })
  ).isRequired,
  stroke: PropTypes.string,
  strokeWidth: PropTypes.number,
  fontSize: PropTypes.number,
  labelColor: PropTypes.string,
}

XAxis.defaultProps = {
  strokeWidth: 1,
  stroke: "#AAA",
  fontSize: 10,
  labelColor: "#666",
}

export default XAxis
