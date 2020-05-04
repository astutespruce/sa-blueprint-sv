import React from "react"

import { Box, Flex, useThemeUI } from "theme-ui"
import Map from "./Map"

const MapContainer = () => {
  const {
    theme: { layout },
  } = useThemeUI()

  return (
    <Flex
      sx={{
        height: "100%",
      }}
    >
      <Box
        sx={{
          height: "100%",
          flexGrow: 1,
          flexShrink: 0,
          flexBasis: layout.sidebar.width,
        }}
      >
        sidebar goes here
      </Box>
      <Box sx={{ bg: "#AAA", flex: "1 1 auto", width: "100%" }} />
      {/* <Map /> */}
    </Flex>
  )
}

export default MapContainer
