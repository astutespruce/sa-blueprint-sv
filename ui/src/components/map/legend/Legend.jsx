import React from "react"
import PropTypes from "prop-types"
import { Box, Flex, Text } from "theme-ui"

import LegendElement from "./LegendElement"

const desktopCSS = {
  flexDirection: "column",
}

const mobileCSS = {
  alignItems: "flex-end",
  justifyContent: "space-between",
}

const Legend = ({ label, elements, isMobile }) => {
  return (
    <Box sx={{ fontSize: isMobile ? 0 : 1 }}>
      {label ? (
        <Text sx={{ lineHeight: 1, fontWeight: "bold" }}>{label}</Text>
      ) : null}
      <Flex sx={isMobile ? mobileCSS : desktopCSS}>
        {elements.map(element => (
          <Box
            key={element.label}
            sx={{
              mt: "0.5rem",
            }}
          >
            <LegendElement {...element} />
          </Box>
        ))}
      </Flex>
    </Box>
  )
}
Legend.propTypes = {
  label: PropTypes.string,
  elements: PropTypes.arrayOf(PropTypes.shape(LegendElement.propTypes))
    .isRequired,
  isMobile: PropTypes.bool,
}

Legend.defaultProps = {
  label: null,
  isMobile: false,
}

export default Legend
