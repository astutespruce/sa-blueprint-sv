import React from "react"
import { Flex, Image, Heading } from "theme-ui"

import { OutboundLink } from "components/link"
import LogoURL from "images/sa_logo.png"
import HeaderButtons from "./HeaderButtons"
import { useBreakpoints } from "./Breakpoints"

const Header = () => {
  const breakpoint = useBreakpoints()

  return (
    <Flex
      as="header"
      sx={{
        justifyContent: "space-between",
        alignItems: "center",
        py: "0.3rem",
        pl: "0.5rem",
        pr: "1rem",
        bg: "primary",
        color: "#FFF",
        zIndex: 1,
        boxShadow: "0 2px 6px #333",
      }}
    >
      <Flex
        sx={{
          alignItems: "center",
        }}
      >
        <OutboundLink
          to="http://www.southatlanticlcc.org/blueprint/"
          sx={{
            textDecoration: "none",
            lineHeight: 0,
            flex: "0 0 auto",
            display: "block",
          }}
        >
          <Image
            src={LogoURL}
            sx={{
              mr: "0.5rem",
              width: "2rem",
              height: "2rem",
            }}
          />
        </OutboundLink>

        <OutboundLink
          to="http://www.southatlanticlcc.org/blueprint/"
          sx={{ textDecoration: "none", display: "block", color: "#FFF" }}
        >
          <Flex
            sx={{
              flexWrap: "wrap",
              alignItems: ["flex-start", "flex-start", "baseline"],
              flexDirection: ["column", "column", "row"],
            }}
          >
            <Heading
              as="h1"
              sx={{
                fontWeight: "normal",
                fontSize: [0, 1, 4],
                lineHeight: 1,
                margin: "0 0.5rem 0 0",
                breakInside: "avoid",
                flex: "0 1 auto",
              }}
            >
              South Atlantic
            </Heading>
            <Heading
              as="h1"
              sx={{
                margin: "0 0.5rem 0 0",
                fontWeight: "normal",
                lineHeight: 1,
                fontSize: [2, 3, 4],
                breakInside: "avoid",
                flexGrow: 0,
                flexShrink: 0,
                flexBasis: ["100%", "unset"],
              }}
            >
              Conservation Blueprint 2.x
            </Heading>
            <Heading
              as="h1"
              sx={{
                margin: 0,
                fontWeight: "normal",
                lineHeight: 1,
                fontSize: [0, 0, 2],
                breakInside: "avoid",
                flexGrow: 0,
                flexShrink: 0,
                flexBasis: ["100%", "unset"],
              }}
            >
              Simple Viewer
            </Heading>
          </Flex>
        </OutboundLink>
      </Flex>
      {breakpoint >= 1 && <HeaderButtons />}
    </Flex>
  )
}

export default Header
