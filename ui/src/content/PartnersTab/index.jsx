import React from 'react'
import PropTypes from 'prop-types'

import { Box, Divider, Heading, Text } from 'theme-ui'

import Ownership from './Ownership'
import Protection from './Protection'
import LTAList from './LTAList'

const PartnersTab = ({
  type,
  analysisAcres,
  ownership,
  protection,
  protectedAreas,
  counties,
}) => {
  if (type === 'marine lease block') {
    return (
      <Box sx={{ py: '2rem', pl: '1rem', pr: '2rem' }}>
        <Text sx={{ color: 'grey.7' }}>
          No information on ownership or protection status is available for
          marine units.
        </Text>
      </Box>
    )
  }

  const hasOwnership = ownership && Object.keys(ownership).length > 0
  const hasProtection = protection && Object.keys(protection).length > 0
  const hasCounties = counties && Object.keys(counties).length > 0
  const hasProtectedAreas = protectedAreas && protectedAreas.length > 0

  console.log('has protected areas', hasProtectedAreas)

  if (type === 'pixel' && !(hasOwnership || hasProtection)) {
    return (
      <Box sx={{ py: '2rem', pl: '1rem', pr: '2rem' }}>
        <Text sx={{ color: 'grey.7' }}>
          No information on ownership or protection status is available.
        </Text>
      </Box>
    )
  }

  return (
    <Box sx={{ py: '2rem', pl: '1rem', pr: '2rem' }}>
      <Box as="section">
        <Heading as="h3">Conserved Lands Ownership</Heading>
        {ownership === null ? (
          <Text sx={{ color: 'grey.7' }}>No information available.</Text>
        ) : (
          <Ownership ownership={ownership} />
        )}
      </Box>

      <Divider variant="styles.hr.light" sx={{ my: '3rem' }} />

      <Box as="section">
        <Heading as="h3">Land Protection Status</Heading>
        {protection === null ? (
          <Text sx={{ color: 'grey.7' }}>No information available.</Text>
        ) : (
          <Protection protection={protection} />
        )}
      </Box>

      {hasProtectedAreas ? (
        <>
          <Divider variant="styles.hr.light" sx={{ my: '3rem' }} />

          <Box as="section">
            <Heading as="h3">Protected Areas</Heading>
            <Box as="ul" sx={{ mt: '0.5rem' }}>
              {protectedAreas.map(({ name, owner }, i) => (
                <li key={`${name}_${owner}_${i}`}>
                  {name || 'Name unknown'} ({owner || 'unknown owner'})
                </li>
              ))}
            </Box>
          </Box>
        </>
      ) : null}

      {hasCounties ? (
        <>
          <Divider variant="styles.hr.light" sx={{ my: '3rem' }} />

          <Box as="section">
            <Heading as="h3">Land Trusts by County</Heading>
            {counties === null ? (
              <Text sx={{ color: 'grey.7' }}>No information available.</Text>
            ) : (
              <LTAList counties={counties} />
            )}
          </Box>
        </>
      ) : null}
    </Box>
  )
}

PartnersTab.propTypes = {
  type: PropTypes.string.isRequired,
  ownership: PropTypes.objectOf(PropTypes.number),
  protection: PropTypes.objectOf(PropTypes.number),
  protectedAreas: PropTypes.arrayOf(
    PropTypes.shape({
      name: PropTypes.string,
      owner: PropTypes.string,
    })
  ),
  counties: PropTypes.objectOf(PropTypes.arrayOf(PropTypes.string)),
}

PartnersTab.defaultProps = {
  ownership: null,
  protection: null,
  protectedAreas: null,
  counties: null,
}

export default PartnersTab
