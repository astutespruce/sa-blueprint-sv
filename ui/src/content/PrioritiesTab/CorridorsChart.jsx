import React from 'react'
import PropTypes from 'prop-types'
import { PieChart } from 'react-minimal-pie-chart'
import { Flex } from 'theme-ui'

import { PieChartLegend } from 'components/chart'

import { sum } from 'util/data'

const chartWidth = 150

const CorridorsChart = ({ categories, corridors, remainder }) => {
  const corridorChartData = corridors
    .map((percent, i) => {
      const { label, color } = categories[i]
      return {
        value: percent,
        label,
        color,
      }
    })
    .filter(({ value }) => value > 0)
    .reverse()

  const corridorsTotal = sum(corridors)

  if (corridorsTotal < 100 - remainder) {
    corridorChartData.push({
      value: 100 - remainder - corridorsTotal,
      color: '#ffebc2',
      label: 'Not a hub or corridor',
    })
  }

  if (remainder >= 1) {
    corridorChartData.push({
      value: remainder,
      color: '#EEE',
      label: 'Outside South Atlantic Blueprint',
    })
  }

  return (
    <Flex sx={{ alignItems: 'center', mt: '2rem' }}>
      <PieChart
        data={corridorChartData}
        lineWidth={60}
        radius={chartWidth / 4 - 2}
        style={{
          width: chartWidth,
          flex: '0 1 auto',
        }}
      />

      <PieChartLegend elements={corridorChartData} />
    </Flex>
  )
}

CorridorsChart.propTypes = {
  categories: PropTypes.arrayOf(
    PropTypes.shape({
      label: PropTypes.string.isRequired,
      color: PropTypes.string.isRequired,
    })
  ).isRequired,
  corridors: PropTypes.arrayOf(PropTypes.number),
  remainder: PropTypes.number,
}

CorridorsChart.defaultProps = {
  corridors: [],
  remainder: 0,
}

export default CorridorsChart
