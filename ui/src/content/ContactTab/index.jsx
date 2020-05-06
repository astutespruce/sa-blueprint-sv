import React from "react"
import { Box, Heading } from "theme-ui"

import Feedback from "./Feedback"
import Contact from "./Contact"

export { Feedback, Contact }

const index = () => {
  return (
    <>
      <Box as="section">
        <Heading as="h3" sx={{ mb: "0.5rem" }}>
          Give your feedback to Blueprint staff
        </Heading>
        <Feedback />
      </Box>

      <Box as="section">
        <Heading as="h3" sx={{ mb: "0.5rem" }}>
          Contact Blueprint staff for help using the Blueprint
        </Heading>
        <Contact />
      </Box>
    </>
  )
}

export default index
