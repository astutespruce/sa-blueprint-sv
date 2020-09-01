import React, { useCallback } from "react"
import PropTypes from "prop-types"
import { Box } from "theme-ui"
import { scaleLinear } from "d3-scale"

import { extent } from "util/data"
import { formatNumber } from "util/format"

import Points from "./Points"
import Line from "./Line"
import XAxis from "./XAxis"
import YAxis from "./YAxis"

const Chart = ({
  data,
  width,
  height,
  margin,
  xTicks,
  yTicks,
  lineColor,
  lineWidth,
  pointRadius,
  pointStrokeColor,
  pointStrokeWidth,
  pointFillColor,
  fontSize,
}) => {
  const [minX, maxX] = extent(data.map(({ x }) => x))
  const [minY, maxY] = extent(data.map(({ y }) => y))

  console.log("bounds", minX, maxX, minY, maxY)
  console.log("dims", width, height)

  // project points into the drawing area
  // (note that scales are flipped here so that 0,0 is bottom left)
  const xScale = scaleLinear()
    .domain([minX, maxX])
    .range([0, width - margin.right - margin.left])
    .nice()

  const yScale = scaleLinear()
    .domain([minY, maxY])
    .range([height - margin.bottom, margin.top])
    .nice()

  const points = data.map(({ x, y, ...rest }) => ({
    ...rest,
    x: xScale(x),
    y: yScale(y),
  }))

  const xAxisTicks = xScale
    .ticks(xTicks)
    .map(x => ({ x: xScale(x), label: formatNumber(x) }))

  const yAxisTicks = yScale
    .ticks(yTicks)
    .map(y => ({ y: yScale(y), label: formatNumber(y) }))

  console.log("x ticks", xAxisTicks)

  return (
    <svg
      style={{
        display: "block",
        overflow: "visible",
      }}
      viewBox={`0 0 ${width} ${height}`}
    >
      <g transform={`translate(${margin.left},${margin.top})`}>
        <g transform={`translate(0, ${height - margin.bottom})`}>
          <XAxis ticks={xAxisTicks} fontSize={fontSize} />
        </g>
        <YAxis ticks={yAxisTicks} fontSize={fontSize} />

        {lineWidth ? (
          <Line points={points} stroke={lineColor} strokeWidth={lineWidth} />
        ) : null}

        {pointRadius ? (
          <Points
            points={points}
            radius={pointRadius}
            stroke={pointStrokeColor}
            strokeWidth={pointStrokeWidth}
            fill={pointFillColor}
          />
        ) : null}
      </g>
    </svg>
  )
}

Chart.propTypes = {
  data: PropTypes.arrayOf(
    PropTypes.shape({
      x: PropTypes.number.isRequired,
      y: PropTypes.number.isRequired,
      label: PropTypes.string,
    })
  ).isRequired,
  width: PropTypes.number.isRequired,
  height: PropTypes.number.isRequired,
  xTicks: PropTypes.number,
  yTicks: PropTypes.number,
  lineColor: PropTypes.string,
  lineWidth: PropTypes.number,
  pointStrokeColor: PropTypes.string,
  pointStrokeWidth: PropTypes.string,
  pointFillColor: PropTypes.string,
  pointRadius: PropTypes.number,
  fontSize: PropTypes.number,
  margin: PropTypes.objectOf(PropTypes.number),
}

Chart.defaultProps = {
  xTicks: null,
  yTicks: null,
  lineWidth: 1,
  pointRadius: 4,
  fontSize: 10,
  margin: {
    left: 40,
    right: 40,
    bottom: 30,
    top: 10,
  },
}

export default Chart
