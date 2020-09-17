import React from 'react'
import PropTypes from 'prop-types'

import { PieChart } from 'react-minimal-pie-chart'
import { Box, Flex, Divider, Heading, Text } from 'theme-ui'

import { PieChartLegend } from 'components/chart'
import { useBlueprintPriorities, useCorridors } from 'components/data'

import { sum } from 'util/data'

const PrioritiesTab = ({ blueprint, corridors }) => {
  const { all: priorityCategories } = useBlueprintPriorities()
  const corridorCategories = useCorridors()

  const chartWidth = 180

  const blueprintChartData = blueprint
    .slice()
    .reverse()
    .map((percent, i) => ({
      value: percent,
      ...priorityCategories[i],
    }))
    .filter(({ value }) => value > 0)

  const blueprintTotal = sum(blueprint)
  let remainder = 0

  if (blueprintTotal < 100) {
    remainder = 100 - blueprintTotal
    blueprintChartData.push({
      value: remainder,
      color: '#EEE',
      label: 'Outside South Atlantic Blueprint',
    })
  }

  const corridorChartData = corridors
    .map((percent, i) => {
      const { label, color } = corridorCategories[i]
      return {
        value: percent,
        label: label.endsWith('Corridors') ? `${label}*` : label,
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

  if (remainder > 0) {
    corridorChartData.push({
      value: remainder,
      color: '#EEE',
      label: 'Outside South Atlantic Blueprint',
    })
  }

  return (
    <Box sx={{ py: '2rem', pl: '1rem', pr: '2rem' }}>
      <Box as="section">
        <Heading as="h3">Blueprint 2020 Priority</Heading>
        <Text sx={{ color: 'grey.7' }}>for shared conservation action</Text>

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
      </Box>

      {corridorChartData.length > 0 ? (
        <>
          <Divider variant="styles.hr.light" sx={{ my: '3rem' }} />
          <Box as="section">
            <Heading as="h3">Hubs &amp; Corridors</Heading>

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
            <Text sx={{ mt: '1rem', fontSize: 1, color: 'grey.7' }}>
              *Note: Includes the full extent of corridors. The Blueprint
              corridors class includes only corridors not already identified as
              priority.
            </Text>
          </Box>
        </>
      ) : (
        <Text sx={{ textAlign: 'center', color: 'grey.6' }}>
          No hubs or corridors in this area.
        </Text>
      )}
    </Box>
  )
}

PrioritiesTab.propTypes = {
  blueprint: PropTypes.arrayOf(PropTypes.number),
  corridors: PropTypes.arrayOf(PropTypes.number),
}

PrioritiesTab.defaultProps = {
  blueprint: [],
  corridors: [],
}

export default PrioritiesTab
