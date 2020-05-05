import React from "react"

import { Box, Heading, Text } from "theme-ui"
import { OutboundLink } from "components/Link"

const Intro = () => {
  return (
    <Box as="section">
      <Heading as="h3" sx={{ mb: "0.5rem" }}>
        Welcome to the South Atlantic Conservation Blueprint Simple Viewer
      </Heading>

      <p>
        The{" "}
        <OutboundLink to="http://www.southatlanticlcc.org/blueprint/">
          Conservation Blueprint
        </OutboundLink>{" "}
        is a living spatial plan to conserve natural and cultural resources for
        future generations. It identifies priority areas for shared conservation
        action. Blueprint 2.x is completely data-driven, prioritizing the lands
        and waters of the South Atlantic region based on ecosystem indicator
        models and a connectivity analysis. Better indicator condition suggests
        higher ecosystem integrity and higher importance for natural and
        cultural resources across all ecosystems collectively. So far, more than
        500 people from 150 organizations actively participated in the
        collaborative development of the Blueprint.
        <br />
        <br />
        This <b>Simple Viewer</b> summarizes the Blueprint priorities and
        supporting information within subwatersheds and marine lease blocks. In
        a new pixel mode, you can also explore pixel-level details of what
        indicators are driving the Blueprint priorities.
      </p>
    </Box>
  )
}

export default Intro
