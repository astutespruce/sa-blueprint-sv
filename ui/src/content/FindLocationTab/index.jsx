import React from "react"
import { Box, Heading } from "theme-ui"

const FindLocationTab = () => {
  return (
    <Box as="section" sx={{ py: "1.5rem", pl: "1rem", pr: "2rem" }}>
      <Heading as="h3" sx={{ mb: "0.5rem" }}>
        Find a location on the map
      </Heading>
      <p>Find location widget goes here</p>
    </Box>
  )
}

export default FindLocationTab
