import React from "react"
import { Container, Box, Heading } from "theme-ui"
import { ExclamationTriangle } from "emotion-icons/fa-solid"

const UnsupportedBrowser = () => (
  <Container>
    <Box
      sx={{
        m: "2rem",
        p: "2rem",
      }}
    >
      <Heading as="h1" sx={{ color: "#FFF" }}>
        <ExclamationTriangle height="2rem" width="2rem" sx={{ mr: "0.5rem" }} />
        Unfortunately, you are using an unsupported version of Internet
        Explorer.
        <br />
        <br />
        Please use a modern browser such as Google Chrome, Firefox, or Microsoft
        Edge.
      </Heading>
    </Box>
  </Container>
)

export default UnsupportedBrowser
