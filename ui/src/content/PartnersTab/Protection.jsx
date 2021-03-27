import React from 'react'
import PropTypes from 'prop-types'
import { CheckCircle } from '@emotion-icons/fa-regular'
import { Box, Flex, Text } from 'theme-ui'

import { PercentBarChart } from 'components/chart'
import { useOwnership } from 'components/data'
import { OutboundLink } from 'components/link'
import { sum } from 'util/data'

const Protection = ({ type, protection }) => {
  const { protection: PROTECTION } = useOwnership()

  const bars = PROTECTION.map((category) => ({
    ...category,
    percent: protection ? protection[category.id] || 0 : 0,
  }))

  const remainder = 100 - sum(bars.map(({ percent }) => percent))
  if (remainder > 0) {
    bars.push({
      id: 'not_conserved',
      label: 'Not conserved',
      color: 'grey.5',
      percent: remainder,
    })
  }

  if (type === 'pixel') {
    return (
      <Box sx={{ ml: '0.5rem', mt: '0.5rem' }}>
        {bars.map(({ id, label, percent }) => (
          <Flex
            key={id}
            sx={{
              alignItems: 'baseline',
              justifyContent: 'space-between',
              pl: '0.5rem',
              borderBottom: '1px solid',
              borderBottomColor: 'grey.2',
              pb: '0.25rem',
              '&:not(:first-of-type)': {
                mt: '0.25rem',
              },
            }}
          >
            <Text
              sx={{
                flex: '1 1 auto',
                color: percent > 0 ? 'text' : 'grey.6',
                fontWeight: percent > 0 ? 'bold' : 'normal',
              }}
            >
              {label}
            </Text>
            {percent === 0 ? (
              <Text sx={{ flex: '0 0 auto', fontSize: 0, color: 'grey.6' }}>
                (absent)
              </Text>
            ) : (
              <Box sx={{ flex: '0 0 auto' }}>
                <CheckCircle size="1em" />
              </Box>
            )}
          </Flex>
        ))}
      </Box>
    )
  }

  return (
    <>
      {bars.map((bar) => (
        <PercentBarChart
          key={bar.id}
          {...bar}
          sx={{ mt: '0.5rem', mb: '1rem' }}
        />
      ))}

      <Text sx={{ color: 'grey.7', fontSize: 1 }}>
        Land protection status is derived from the TNC{' '}
        <OutboundLink to="https://www.conservationgateway.org/ConservationByGeography/NorthAmerica/UnitedStates/edc/reportsdata/terrestrial/secured/Pages/default.aspx">
          Secured Lands Database
        </OutboundLink>{' '}
        (2018 Edition).
      </Text>
    </>
  )
}

Protection.propTypes = {
  type: PropTypes.string.isRequired,
  protection: PropTypes.objectOf(PropTypes.number),
}

Protection.defaultProps = {
  protection: {},
}

export default Protection
