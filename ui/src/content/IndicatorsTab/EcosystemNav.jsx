import React, { useCallback } from "react"
import PropTypes from "prop-types"

import { Box, Flex, Image } from "theme-ui"

import { EcosystemPropType } from "./Ecosystem"

const EcosystemNav = ({ ecosystemId, ecosystems, onClick }) => {
  const getIcon = id => {
    const icon = require(`images/${id}.svg`)
    return icon
  }

  const baseCSS = {
    boxSizing: "content-box",
    bg: "#FFF",
    cursor: "pointer",
    px: "0.25em",
    flex: "0 0 auto",
  }

  const defaultCSS = {
    ...baseCSS,
    width: "1.5rem",
    height: "1.5rem",
    filter: "grayscale(50%)",
    borderRadius: "1.5rem",
    opacity: 0.4,
  }
  const activeCSS = {
    ...baseCSS,
    width: "2rem",
    height: "2rem",
    borderRadius: "2rem",
  }

  const handleClick = useCallback(
    id => () => {
      onClick(id)
    },
    []
  )

  return (
    <Flex
      sx={{
        alignItems: "center",
        justifyContent: "center",
        py: "0.5rem",
        px: "0.25rem",
        bg: "grey.0",
      }}
    >
      {ecosystems.map(({ id }) => (
        <Image
          key={id}
          src={getIcon(id)}
          sx={id === ecosystemId ? activeCSS : defaultCSS}
          onClick={handleClick(id)}
        />
      ))}
    </Flex>
  )
}

EcosystemNav.propTypes = {
  ecosystemId: PropTypes.string.isRequired,
  ecosystems: PropTypes.arrayOf(
    PropTypes.shape({
      ...EcosystemPropType,
    })
  ).isRequired,
  onClick: PropTypes.func.isRequired,
}

export default EcosystemNav
