import React from 'react'
import { Alert, Box, Paragraph } from 'theme-ui'

import { OutboundLink } from 'components/link'

const Intro = () => (
  <>
    <Box as="section">
      <Alert sx={{ bg: 'blue.1', fontWeight: 'normal', py: '0.5em' }}>
        <Paragraph sx={{ fontSize: 1 }}>
          <b>Head&apos;s up!</b>
          <br />
          This fall, the 2022 version of the Southeast Conservation Blueprint
          will replace the South Atlantic Blueprint. As part of this update, the{' '}
          <OutboundLink to="https://blueprint.geoplatform.gov/southeast/">
            Southeast Blueprint Explorer (currently in beta)
          </OutboundLink>{' '}
          will expand its functionality and replace the South Atlantic Blueprint
          Simple Viewer to provide more features across a broader area. Stay
          tuned!
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
        supporting information within subwatersheds (HUC12) and marine lease
        blocks as well as pixel-level details of what indicators are driving the
        Blueprint priorities.
      </p>
    </Box>
  </>
)

export default Intro
