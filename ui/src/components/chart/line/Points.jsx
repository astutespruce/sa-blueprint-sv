import React, { useCallback } from "react"
import PropTypes from "prop-types"

const Points = ({
  points,
  radius,
  stroke,
  strokeWidth,
  fill,
  hoverRadius,
  onHover,
}) => {
  const handleMouseOver = useCallback(e => {
    console.log("mouseover", e.target)
  })

  return (
    <g>
      {points.map(({ x, y }) => (
        <g key={`${x}_${y}`}>
          <circle
            r={radius}
            cx={x}
            cy={y}
            style={{ fill, stroke, strokeWidth }}
          />
          <circle
            key={`${x}_${y}`}
            r={hoverRadius || radius * 2}
            cx={x}
            cy={y}
            fill="transparent"
            stroke="none"
            style={{ cursor: "pointer" }}
            onMouseEnter={handleMouseOver}
          />
        </g>
      ))}
    </g>
  )
}

Points.propTypes = {
  points: PropTypes.arrayOf(
    PropTypes.shape({
      x: PropTypes.number.isRequired,
      y: PropTypes.number.isRequired,
      label: PropTypes.string,
    })
  ).isRequired,
  stroke: PropTypes.string,
  strokeWidth: PropTypes.number,
  fill: PropTypes.string,
  hoverRadius: PropTypes.number,
}

Points.defaultProps = {
  radius: 4,
  stroke: null,
  strokeWidth: 0,
  fill: "#AAA",
  hoverRadius: null,
}

// TODO: memoize
export default Points
