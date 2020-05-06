import React, { useState, useCallback } from "react"
import { Box, Flex, useThemeUI } from "theme-ui"

import { useBreakpoints } from "components/layout"
import { InfoTab, ContactTab, FindLocationTab } from "content"
import { Tabs } from "components/tabs"

import Map from "./Map"

const MapContainer = () => {
  const {
    theme: { layout },
  } = useThemeUI()

  const breakpoint = useBreakpoints()

  const [{ tab }, setState] = useState({
    tab: breakpoint === 0 ? "map" : "info",
  })

  const handleTabChange = useCallback(tab => {
    console.log("Set tab", tab)
    setState(prevState => ({
      ...prevState,
      tab,
    }))
  })

  let content = null
  if (breakpoint === 0) {
    switch (tab) {
      case "info": {
        content = <InfoTab />
        break
      }
      case "map": {
        // don't show anything
        content = null
        break
      }
      case "find": {
        content = <FindLocationTab />
        break
      }
      case "contact": {
        content = <ContactTab />
        break
      }
    }
  } else {
    content = <InfoTab />
  }

  return (
    <Flex
      sx={{
        height: "100%",
        flexDirection: "column",
      }}
    >
      <Flex
        sx={{
          height: "100%",
          flex: "1 1 auto",
          overflowY: "hidden",
        }}
      >
        <Box
          sx={{
            display: content === null ? "none" : "block",
            height: "100%",
            flexGrow: 1,
            flexShrink: 0,
            flexBasis: layout.sidebar.width,
            py: "1rem",
            pl: "1rem",
            pr: "2rem",
            overflowY: "auto",
            borderRightColor: layout.sidebar.borderRightColor,
            borderRightWidth: layout.sidebar.borderRightWidth,
            borderRightStyle: "solid",
          }}
        >
          {content}
        </Box>

        {/* Map placeholder */}
        <Box
          sx={{
            background: "linear-gradient(0deg, #08AEEA 0%, #2AF598 100%)",
            flex: "1 1 auto",
            width: "100%",
          }}
        />
        {/* <Map /> */}
      </Flex>

      {breakpoint === 0 && (
        <Box
          sx={{
            flex: "0 0 auto",
            borderTop: "1px solid",
            borderTopColor: "grey.9",
          }}
        >
          <Tabs
            tabs={[
              { id: "info", label: "Info" },
              { id: "map", label: "Map" },
              { id: "find", label: "Find Location" },
              { id: "contact", label: "Contact" },
            ]}
            activeTab={tab}
            activeVariant="tabs.mobileActive"
            variant="tabs.mobile"
            onChange={handleTabChange}
          />
        </Box>
      )}
    </Flex>
  )
}

export default MapContainer
