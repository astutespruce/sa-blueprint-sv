import React from 'react'
import PropTypes from 'prop-types'
import { PieChart } from 'react-minimal-pie-chart'
import { Flex } from 'theme-ui'

import { PieChartLegend } from 'components/chart'

const chartWidth = 150

const BlueprintChart = ({ categories, blueprint, remainder }) => {
  const blueprintChartData = blueprint
    .map((percent, i) => ({
      ...categories[i],
      value: percent,
    }))
    .filter(({ value }) => value > 0)
    .reverse()

  if (remainder) {
    blueprintChartData.push({
      value: remainder,
      color: '#EEE',
      label: 'Outside South Atlantic Blueprint',
    })
  }

  return (
    <Flex sx={{ alignItems: 'center', mt: '2rem' }}>
      <PieChart
        data={blueprintChartData}
        lineWidth={60}
        radius={chartWidth / 4 - 2}
        style={{
          width: chartWidth,
          flex: '0 1 auto',
        }}
      />

      <PieChartLegend elements={blueprintChartData} />
    </Flex>
  )
}

BlueprintChart.propTypes = {
  categories: PropTypes.arrayOf(
    PropTypes.shape({
      label: PropTypes.string.isRequired,
      color: PropTypes.string.isRequired,
    })
  ).isRequired,
  blueprint: PropTypes.arrayOf(PropTypes.number),
  remainder: PropTypes.number,
}

BlueprintChart.defaultProps = {
  blueprint: [],
  remainder: 0,
}

export default BlueprintChart
