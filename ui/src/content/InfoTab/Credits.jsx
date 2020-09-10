import React from 'react'
import { Box, Text } from 'theme-ui'

import { OutboundLink } from 'components/link'

const Credits = () => {
  return (
    <Box as="section" sx={{ pb: '2rem' }}>
      <Text as="p" sx={{ fontSize: 1 }}>
        <b>Citation:</b> The South Atlantic Conservation Blueprint 2020.
        <br />
        <br />
        This application was developed by{' '}
        <OutboundLink to="http://www.southatlanticlcc.org/">
          South Atlantic Conservation Blueprint
        </OutboundLink>{' '}
        and{' '}
        <OutboundLink to="https://astutespruce.com">
          Astute Spruce, LLC
        </OutboundLink>{' '}
        based on support from the U.S. Fish and Wildlife Service under the{' '}
        <OutboundLink to="http://secassoutheast.org/">
          Southeast Conservation Adaptation Strategy
        </OutboundLink>
        . Earlier versions of this application were developed in partnership
        with the{' '}
        <OutboundLink to="https://consbio.org">
          Conservation Biology Institute
        </OutboundLink>
        .
      </Text>
    </Box>
  )
}

export default Credits
