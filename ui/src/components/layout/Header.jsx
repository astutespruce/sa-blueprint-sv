import React from "react"
import { Flex, Image, Heading } from "theme-ui"

import { Link } from "components/Link"
import LogoURL from "images/sa_logo.png"

const Header = () => {
  return (
    <Flex
      as="header"
      sx={{
        alignItems: "center",
        py: "0.3rem",
        pl: "0.25rem",
        pr: "1rem",
        bg: "primary",
        color: "#FFF",
        boxShadow: "0 2px 6px #333",
      }}
    >
      <Image
        src={LogoURL}
        sx={{ mr: "0.5rem", width: "2rem", height: "2rem", flex: "0 0 auto" }}
      />
      <Heading
        as="h1"
        sx={{
          fontWeight: "normal",
          fontSize: [3, 4, 5],
          a: {
            textDecoration: "none",
            color: "#fff",
          },
        }}
      >
        <Link to="/">
          South Atlantic Conservation Blueprint 2.2 - Report Generator
        </Link>
      </Heading>
    </Flex>
  )
}

export default Header
