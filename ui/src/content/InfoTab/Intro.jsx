import React from 'react'
import { Box } from 'theme-ui'

import { OutboundLink } from 'components/link'

const Intro = () => (
  <>
    <Box as="section">
      <p>
        The South Atlantic Conservation Blueprint is a living spatial plan to
        conserve natural and cultural resources for future generations. It
        identifies shared conservation priorities across the South Atlantic
        region.
        <br />
        <br />
        The Blueprint is a data-driven plan based on terrestrial, freshwater,
        and marine indicators. It uses the current condition of those indicators
        to prioritize the most important areas for natural and cultural
        resources across the South Atlantic geography.
        <br />
        <br />
        For more information, visit{' '}
        <OutboundLink to="http://www.southatlanticlcc.org/blueprint/">
          the Blueprint webpage
        </OutboundLink>
        . On that page, you can see who’s using the Blueprint to inform
        conservation action and investment.
        <br />
        <br />
        If you want to overlay additional datasets, view indicator layers, and
        download Blueprint data, visit{' '}
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
