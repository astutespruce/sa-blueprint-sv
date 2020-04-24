import React from "react"
import { Box, Link } from "theme-ui"

import config from "../../../gatsby-config"

const { contactEmail } = config.siteMetadata

const Footer = () => {
  return (
    <Box
      as="footer"
      sx={{
        bg: "primary",
        color: "#FFF",
        mt: "1px",
        py: "0.3rem",
        px: "0.5rem",
        fontSize: "smaller",
      }}
    >
      Need help? We're happy to assist you with all your Blueprint needs. Please{" "}
      <Link sx={{ color: "#FFF" }} href={`mailto:${contactEmail}`}>
        Contact Us
      </Link>
      .
    </Box>
  )
}

export default Footer
