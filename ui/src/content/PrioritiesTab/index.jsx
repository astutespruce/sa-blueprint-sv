import React from 'react'
import PropTypes from 'prop-types'

import { Box, Flex, Divider, Heading, Text } from 'theme-ui'

import { useBlueprintPriorities, useCorridors } from 'components/data'
import { sum } from 'util/data'

import BlueprintChart from './BlueprintChart'
import CorridorsChart from './CorridorsChart'

const PrioritiesTab = ({ type, blueprint, corridors }) => {
  const { all: allPriorities } = useBlueprintPriorities()
  const corridorCategories = useCorridors()

  // Note: incoming priorities are in descending order but percents
  // are stored in ascending order
  const priorityCategories = allPriorities.slice().reverse()

  const remainder = type !== 'pixel' ? Math.max(1, 100 - sum(blueprint)) : 0

  let corridorsColor = '#ffebc2'
  let corridorsLabel = 'Not a hub or corridor'

  if (type === 'pixel' && corridors !== null) {
    corridorsColor = corridorCategories[corridors].color
    corridorsLabel = corridorCategories[corridors].label
  }

  return (
    <Box sx={{ py: '2rem', pl: '1rem', pr: '2rem' }}>
      <Box as="section">
        <Heading as="h3">Blueprint Priority</Heading>
        <Text sx={{ color: 'grey.7' }}>for shared conservation action</Text>

        {type === 'pixel' ? (
          <Flex sx={{ alignItems: 'center', mt: '0.5rem' }}>
            <Box
              sx={{
                width: '2rem',
                height: '1.5rem',
                mr: '0.5rem',
                bg: priorityCategories[blueprint].color,
              }}
            />
            <Text>{priorityCategories[blueprint].label}</Text>
          </Flex>
        ) : (
          <BlueprintChart
            categories={priorityCategories}
            blueprint={blueprint}
            remainder={remainder}
          />
        )}
      </Box>

      <Divider variant="styles.hr.light" sx={{ my: '3rem' }} />
      <Box as="section">
        <Heading as="h3">Hubs &amp; Corridors</Heading>

        {type === 'pixel' ? (
          <Flex sx={{ alignItems: 'center', mt: '0.5rem' }}>
            <Box
              sx={{
                width: '2rem',
                height: '1.5rem',
                mr: '0.5rem',
                bg: corridorsColor,
              }}
            />
            <Text>{corridorsLabel}</Text>
          </Flex>
        ) : (
          <CorridorsChart
            categories={corridorCategories}
            corridors={corridors}
            remainder={remainder}
          />
        )}
        <Text sx={{ mt: '1rem', fontSize: 1, color: 'grey.7' }}>
          *Note: Includes the full extent of corridors. The Blueprint corridors
          class includes only corridors not already identified as priority.
        </Text>
      </Box>
    </Box>
  )
}

PrioritiesTab.propTypes = {
  type: PropTypes.string.isRequired,
  blueprint: PropTypes.oneOfType([
    PropTypes.arrayOf(PropTypes.number),
    PropTypes.number,
  ]),
  corridors: PropTypes.oneOfType([
    PropTypes.arrayOf(PropTypes.number),
    PropTypes.number,
  ]),
}

PrioritiesTab.defaultProps = {
  blueprint: [],
  corridors: [],
}

export default PrioritiesTab
