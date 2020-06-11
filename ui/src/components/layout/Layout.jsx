import React from "react"
import PropTypes from "prop-types"
import { Box, Flex } from "theme-ui"

import { isUnsupported } from "util/dom"
import UnsupportedBrowser from "./UnsupportedBrowser"
import SEO from "./SEO"
import Header from "./Header"
import { BreakpointProvider } from "./Breakpoints"
import { siteMetadata } from "../../../gatsby-config"

const Layout = ({ children, title, overflowY }) => (
  <BreakpointProvider>
    <Flex
      sx={{
        height: "100%",
        flexDirection: "column",
      }}
    >
      <SEO title={title || siteMetadata.title} />
      <Header />
      {isUnsupported ? (
        <UnsupportedBrowser />
      ) : (
        <Box sx={{ flex: "1 1 auto", overflowY, height: "100%" }}>
          {children}
        </Box>
      )}
    </Flex>
  </BreakpointProvider>
)

Layout.propTypes = {
  children: PropTypes.node.isRequired,
  title: PropTypes.string,
  overflowY: PropTypes.string,
}

Layout.defaultProps = {
  title: "",
  overflowY: "auto",
}

export default Layout
