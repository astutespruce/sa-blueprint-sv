import React from 'react'
import { Alert, Box, Paragraph } from 'theme-ui'
import { lighten } from '@theme-ui/color'

import { OutboundLink } from 'components/link'

const Intro = () => (
  <>
    <Box as="section">
      <Alert sx={{ bg: 'blue.1', fontWeight: 'normal', py: '0.5em' }}>
        <Paragraph sx={{ fontSize: 1 }}>
          <b>Head&apos;s up!</b>
          <br />
          The South Atlantic Conservation Blueprint 2021 is now available, but
          not yet integerated into this viewer (we&apos;re working on it!). In
          the meantime, please visit the{' '}
          <OutboundLink to="https://salcc.databasin.org/galleries/f3c66628b531496f8c9b52648a9167ca/">
            Conservation Planning Atlas
          </OutboundLink>
          <br /> for the 2021 version data.
        </Paragraph>
      </Alert>

      <p>
        The South Atlantic Conservation Blueprint is a living spatial plan to
        conserve natural and cultural resources for future generations. It
        prioritizes the lands and waters of the South Atlantic based on the
        current condition of terrestrial, freshwater, and marine indicators.
        Through a connectivity analysis, it also identifies important hubs and
        corridors. More than 700 people from over 200 different organizations
        have participated in its development so far.
        <br />
        <br />
        For more information, visit{' '}
        <OutboundLink to="http://www.southatlanticlcc.org/blueprint/">
          the Blueprint webpage
        </OutboundLink>
        . On that page, you can see who’s using the Blueprint to inform
        conservation action and investment. If you want to overlay additional
        datasets, view indicator layers, and download Blueprint data, visit{' '}
        <OutboundLink to="https://salcc.databasin.org/">
          the Conservation Planning Atlas
        </OutboundLink>{' '}
        (CPA).
        <br />
        <br />
        The Blueprint integrates with neighboring priorities in a Southeast-wide
        plan as part of the{' '}
        <OutboundLink to="http://secassoutheast.org/">
          Southeast Conservation Adaptation Strategy
        </OutboundLink>
        .
      </p>

      <p>
        This <b>Simple Viewer</b> summarizes the Blueprint priorities and
        supporting information within subwatersheds and marine lease blocks as
        well as pixel-level details of what indicators are driving the Blueprint
        priorities.
      </p>
    </Box>
  </>
)

export default Intro
