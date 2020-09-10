/** @jsx jsx */
import React from 'react'
import PropTypes from 'prop-types'
import { useThemeUI, jsx } from 'theme-ui'
import { formatPercent } from 'util/format'

const PercentDonut = ({
  size,
  color,
  centerColor,
  donutWidth,
  percent,
  sx,
}) => {
  const { theme } = useThemeUI()

  const halfsize = size / 2
  const center = halfsize
  const radius = halfsize - donutWidth * 0.5
  const circumference = 2 * Math.PI * radius
  const rotateval = `rotate(-90 ${center},${center})`

  return (
    <svg
      width={`${size}px`}
      height={`${size}px`}
      sx={{ flex: '0 0 auto', ...sx }}
    >
      <circle
        cx={center}
        cy={center}
        r={radius}
        fill={centerColor || theme.colors.grey[9]}
        stroke={theme.colors.grey[2]}
        strokeWidth={donutWidth}
      />
      <circle
        cx={center}
        cy={center}
        r={radius}
        transform={rotateval}
        fill="transparent"
        stroke={color || theme.colors.primary}
        strokeWidth={donutWidth}
        strokeDasharray={`${(percent * circumference) / 100} ${circumference}`}
      />
      <text
        x={halfsize}
        y={halfsize}
        fill="#FFFFFF"
        style={{
          textAnchor: 'middle',
          dominantBaseline: 'central',
        }}
      >
        {formatPercent(percent)}%
      </text>
    </svg>
  )
}

PercentDonut.propTypes = {
  percent: PropTypes.number.isRequired,
  color: PropTypes.string,
  centerColor: PropTypes.string,
  size: PropTypes.number,
  donutWidth: PropTypes.number,
  sx: PropTypes.object,
}

PercentDonut.defaultProps = {
  size: 100,
  color: null,
  centerColor: null,
  donutWidth: 10,
  sx: null,
}

export default PercentDonut
