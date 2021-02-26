import React from 'react'
import PropTypes from 'prop-types'
import { Box, Grid, Flex, Text } from 'theme-ui'

import { PercentBarChart } from 'components/chart'
import { useOwnership } from 'components/data'
import { OutboundLink } from 'components/link'
import { sum } from 'util/data'

const Protection = ({ type, protection }) => {
  const { protection: PROTECTION } = useOwnership()

  // handle null / empty ownership data
  const bars = PROTECTION.filter(({ id }) => (protection || {})[id]).map(
    (category) => ({
      ...category,
      percent: protection[category.id],
    })
  )

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
      <>
        {bars.map(({ id, color, label }) => (
          <Grid
            columns="2rem 1fr"
            sx={{ alignItems: 'center', mt: '0.5rem', lineHeight: 1.2 }}
          >
            <Box
              key={id}
              sx={{
                height: '100%',
                minHeight: '1.5rem',
                width: '100%',
                flex: '0 0 auto',
                bg: color,
              }}
            />
            <Text sx={{ width: '100%' }}>{label}</Text>
          </Grid>
        ))}
      </>
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
