import React from 'react'
import PropTypes from 'prop-types'
import { Alert, Close, Box, Text, Link } from 'theme-ui'
import { ExclamationTriangle } from '@emotion-icons/fa-solid'

import { OutboundLink } from 'components/link'

import config from '../../../gatsby-config'

const { contactEmail } = config.siteMetadata

const UploadError = ({ error, handleClearError }) => (
  <>
    <Alert variant="error" sx={{ mt: '2rem', mb: '4rem', py: '1rem' }}>
      <ExclamationTriangle
        size="2rem"
        style={{
          margin: '0 1rem 0 0',
        }}
      />
      <Box sx={{ mr: '2rem' }}>
        Uh oh! There was an error!
        <br />
        {error ? (
          `The server says: ${error}`
        ) : (
          <>
            <Text as="span">
              Please try again. If that does not work, try a different file or
            </Text>{' '}
            <Link sx={{ color: '#FFF' }} href={`mailto:${contactEmail}`}>
              Contact Us
            </Link>
            .
          </>
        )}
      </Box>

      <Close
        variant="buttons.alertClose"
        ml="auto"
        sx={{ flex: '0 0 auto' }}
        onClick={handleClearError}
      />
    </Alert>

    {error && error.search('does not overlap') !== -1 ? (
      <Box sx={{ my: '2rem' }}>
        Your area of interest may overlap with the Southeast Conservation
        Blueprint.
        <br />
        Please see the{' '}
        <OutboundLink to="https://blueprint.geoplatform.gov/southeast/">
          Southeast Conservation Blueprint Explorer
        </OutboundLink>{' '}
        to generate a similar report for your area of interest.
        <br />
        <br />
        Do you need help? South Atlantic staff are here to support you! Please{' '}
        <Link href={`mailto:${contactEmail}`}>Contact Us</Link>.
        <br />
        We really mean it. It is what we do!
      </Box>
    ) : null}
  </>
)

UploadError.propTypes = {
  error: PropTypes.string,
  handleClearError: PropTypes.func.isRequired,
}

UploadError.defaultProps = {
  error: null,
}

export default UploadError
