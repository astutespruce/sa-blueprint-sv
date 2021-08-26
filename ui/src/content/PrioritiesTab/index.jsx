import React from 'react'
import PropTypes from 'prop-types'
import { Box, Divider, Heading, Text } from 'theme-ui'

import { useBlueprintPriorities, useCorridors } from 'components/data'
import NeedHelp from 'content/NeedHelp'
import { sum } from 'util/data'

import BlueprintChart from './BlueprintChart'
import CorridorsChart from './CorridorsChart'
import PriorityCategories from './PriorityCategories'
import CorridorCategories from './CorridorCategories'

const PrioritiesTab = ({ type, blueprint, corridors }) => {
  const { all: allPriorities } = useBlueprintPriorities()
  const corridorCategories = useCorridors()

  // Note: incoming priorities are in descending order but percents
  // are stored in ascending order
  const priorityCategories = allPriorities.slice().reverse()

  let remainder = 0
  if (type !== 'pixel') {
    remainder = 100 - sum(blueprint)
    if (remainder < 1) {
      remainder = 0
    }
  }

  let hasInland = false
  let hasMarine = false
  if (corridors !== null) {
    if (type === 'pixel') {
      hasInland = corridors <= 1
      hasMarine = corridors > 1 && corridors < 4
    } else {
      hasInland = sum(corridors.slice(0, 2)) > 0
      // Note: value 4 is not present in the summarized data
      hasMarine = sum(corridors.slice(2, corridors.length)) > 0
    }
  }

  const filterCorridors = ({ value }) => {
    if (value === 4) {
      return type === 'pixel'
    }
    if (!hasInland && value <= 1) {
      return false
    }
    if (!hasMarine && value > 1) {
      return false
    }
    return true
  }

  return (
    <Box sx={{ py: '2rem', pl: '1rem', pr: '2rem' }}>
      <Box as="section">
        <Heading as="h3">Blueprint Priority</Heading>
        <Text sx={{ color: 'grey.8' }}>for shared conservation action</Text>

        {type !== 'pixel' ? (
          <BlueprintChart
            categories={priorityCategories}
            blueprint={blueprint}
            remainder={remainder}
          />
        ) : null}

        {remainder < 100 ? (
          <PriorityCategories
            categories={priorityCategories
              .slice()
              .reverse()
              .filter(({ value }) => (type === 'pixel' ? true : value > 0))}
            value={type === 'pixel' ? blueprint : null}
          />
        ) : null}
      </Box>

      <Divider variant="styles.hr.light" sx={{ my: '3rem' }} />
      <Box as="section">
        <Heading as="h3">Hubs &amp; Corridors</Heading>

        {type !== 'pixel' ? (
          <CorridorsChart
            categories={corridorCategories}
            corridors={corridors}
            remainder={remainder}
          />
        ) : null}

        {remainder < 100 ? (
          <CorridorCategories
            categories={corridorCategories.filter(filterCorridors)}
            value={type === 'pixel' ? corridors || 4 : null}
          />
        ) : null}
      </Box>

      <NeedHelp />
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
