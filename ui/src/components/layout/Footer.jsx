import React from "react"
import { Box, Link } from "theme-ui"

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
      <Link sx={{ color: "#FFF" }} href="mailto:hilary_morris@fws.gov">
        Contact Us
      </Link>
      .
    </Box>
  )
}

export default Footer
