import React from 'react'
import { Box } from 'theme-ui'

import { OutboundLink } from 'components/link'

const Intro = () => {
  return (
    <>
      <Box as="section">
        <p>
          The South Atlantic Conservation Blueprint is a living spatial plan to
          conserve natural and cultural resources for future generations. It
          identifies shared conservation priorities across the South Atlantic
          region.
          <br />
          <br />
          The South Atlantic Blueprint is a data-driven plan based on
          terrestrial, freshwater, marine, and cross-ecosystem indicators. It
          uses the current condition of those indicators to prioritize the most
          important areas for natural and cultural resources across the South
          Atlantic geography. Through a connectivity analysis, the Blueprint
          also identifies corridors that link coastal and inland areas and span
          climate gradients. The Blueprint reflects extensive feedback from the
          broader cooperative community, with more than 700 people from over 200
          different organizations actively participating in its development so
          far. The Blueprint integrates with neighboring priorities in a
          Southeast-wide plan as part of the{' '}
          <OutboundLink to="http://secassoutheast.org/">
            Southeast Conservation Adaptation Strategy
          </OutboundLink>
          .
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
        </p>

        <p>
          This <b>Simple Viewer</b> summarizes the Blueprint priorities and
          supporting information within subwatersheds and marine lease blocks as
          well as pixel-level details of what indicators are driving the
          Blueprint priorities.
        </p>
      </Box>
    </>
  )
}

export default Intro
