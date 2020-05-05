import React from "react"
import { Box, Flex, useThemeUI } from "theme-ui"

import { InfoTab } from "content"

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
          p: "1rem",
          overflowY: "auto",
          borderRightColor: layout.sidebar.borderRightColor,
          borderRightWidth: layout.sidebar.borderRightWidth,
          borderRightStyle: "solid",
        }}
      >
        <InfoTab />
      </Box>
      <Box
        sx={{
          background: "linear-gradient(0deg, #08AEEA 0%, #2AF598 100%)",
          flex: "1 1 auto",
          width: "100%",
        }}
      />
      {/* <Map /> */}
    </Flex>
  )
}

export default MapContainer
