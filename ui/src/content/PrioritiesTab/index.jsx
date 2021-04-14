import React from 'react'
import PropTypes from 'prop-types'
import { Box, Flex, Divider, Heading, Text } from 'theme-ui'

import { useBlueprintPriorities, useCorridors } from 'components/data'
import NeedHelp from 'content/NeedHelp'
import { sum } from 'util/data'

import BlueprintChart from './BlueprintChart'
import CorridorsChart from './CorridorsChart'
import PriorityCategories from './PriorityCategories'

const PrioritiesTab = ({ type, blueprint, corridors, ecosystems }) => {
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

  let corridorsColor = '#ffebc2'
  let corridorsLabel = 'Not a hub or corridor'
  let hasInland = false
  let hasMarine = false

  const hasInlandIndicators =
    ecosystems.has('land') || ecosystems.has('freshwater')
  const hasMarineIndicators = ecosystems.has('marine')

  if (corridors !== null) {
    if (type === 'pixel') {
      corridorsColor = corridorCategories[corridors].color
      corridorsLabel = corridorCategories[corridors].label
      hasInland = corridors <= 1
      hasMarine = corridors > 1
    } else {
      hasInland = sum(corridors.slice(0, 2)) > 0
      hasMarine = sum(corridors.slice(2, corridors.length)) > 0
    }
  }

  return (
    <Box sx={{ py: '2rem', pl: '1rem', pr: '2rem' }}>
      <Box as="section">
        <Heading as="h3">Blueprint Priority</Heading>
        <Text sx={{ color: 'grey.7' }}>for shared conservation action</Text>

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
        {hasInland || hasInlandIndicators || type === 'subwatershed' ? (
          <Text sx={{ mt: '1em', fontSize: 1, color: 'grey.7' }}>
            Inland hubs are either large patches (&gt;2,000 ha) of highest
            priority Blueprint areas or large patches of permanently protected
            lands. Inland corridors are the shortest paths that connect these
            hubs while routing through as much Blueprint priority as possible.
          </Text>
        ) : null}
        {hasMarine || hasMarineIndicators || type === 'marine_block' ? (
          <Text sx={{ mt: '1em', fontSize: 1, color: 'grey.7' }}>
            Marine hubs are either large patches (&gt;2,000 ha) of highest
            priority Blueprint areas or large patches of open water estuaries.
            Marine corridors are the shortest paths that connect these hubs
            while routing through as much Blueprint priority as possible.
          </Text>
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
  ecosystems: PropTypes.instanceOf(Set),
}

PrioritiesTab.defaultProps = {
  blueprint: [],
  corridors: [],
  ecosystems: new Set(),
}

export default PrioritiesTab
