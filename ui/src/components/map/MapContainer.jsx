import React, {
  useState,
  useCallback,
  useRef,
  useEffect,
  useLayoutEffect,
} from "react"
import { Box, Flex, useThemeUI } from "theme-ui"

import { useBreakpoints, useSelectedUnit } from "components/layout"
import {
  InfoTab,
  ContactTab,
  FindLocationTab,
  PrioritiesTab,
  IndicatorsTab,
  ThreatsTab,
  PartnersTab,
} from "content"
import { Tabs as MobileTabs } from "components/layout/mobile"
import {
  SelectedUnitHeader as DesktopSelectedUnitHeader,
  Tabs as DesktopTabs,
} from "components/layout/desktop"

import { useSearch } from "components/search"

import Map from "./Map"

const MapContainer = () => {
  const {
    theme: { layout },
  } = useThemeUI()

  const { location } = useSearch()

  const contentNode = useRef(null)

  // flag so we only do some things on initial loading
  const isDuringLoad = useRef(true)

  const breakpoint = useBreakpoints()
  const isMobile = breakpoint === 0

  const { selectedUnit, selectUnit, deselectUnit } = useSelectedUnit()

  const [{ tab }, setState] = useState({
    tab: breakpoint === 0 ? "map" : "info",
  })

  useEffect(() => {
    isDuringLoad.current = false
  }, [])

  useLayoutEffect(() => {
    // If selected unit changed from null to unit, or unit to null,
    // we need to update the tabs.
    let nextTab = tab
    if (selectedUnit === null) {
      nextTab = tab === "unit-map" || isMobile ? "map" : "info"
    } else {
      if (tab === "map") {
        nextTab = "unit-map"
      } else if (!tab.startsWith("unit-")) {
        nextTab = "unit-priorities"
      }
    }

    if (nextTab !== tab) {
      setState(prevState => ({
        ...prevState,
        tab: nextTab,
      }))
      // scroll content to top
      contentNode.current.scrollTop = 0
    }
  }, [selectedUnit])

  // handle window resize from mobile to desktop, so that we show content again
  // if map tab previously selected
  useEffect(() => {
    if (breakpoint > 0 && !isDuringLoad) {
      const nextTab = tab === "map" ? "info" : "unit-priorities"
      setState(prevState => ({ ...prevState, tab: nextTab }))
    }
  }, [breakpoint])

  // if location is set in mobile view, automatically switch to map tab
  useEffect(() => {
    if (isMobile && location !== null && tab !== "map") {
      setState(prevState => ({ ...prevState, tab: "map" }))
    }
  }, [location, selectedUnit, isMobile])

  const handleTabChange = useCallback(tab => {
    setState(prevState => ({
      ...prevState,
      tab,
    }))
    // scroll content to top
    contentNode.current.scrollTop = 0
  })

  let content = null
  if (selectedUnit === null) {
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
    const {
      type: unitType,
      acres: unitAcres,
      blueprint,
      blueprint_total: blueprintAcres,
      shape_mask: analysisAcres,
      corridors,
      indicators,
      slr,
      urban,
      ownership,
      protection,
      counties,
    } = selectedUnit

    switch (tab) {
      case "unit-map": {
        // don't show anything
        content = null
        break
      }
      case "unit-priorities": {
        content = (
          <PrioritiesTab
            blueprint={blueprint}
            corridors={corridors}
            blueprintAcres={blueprintAcres}
          />
        )
        break
      }
      case "unit-indicators": {
        content = (
          <IndicatorsTab
            unitType={unitType}
            blueprintAcres={blueprintAcres}
            analysisAcres={analysisAcres}
            indicators={indicators}
          />
        )
        break
      }
      case "unit-threats": {
        content = <ThreatsTab unitType={unitType} slr={slr} urban={urban} />
        break
      }
      case "unit-partners": {
        content = (
          <PartnersTab
            unitType={unitType}
            analysisAcres={unitAcres}
            ownership={ownership}
            protection={protection}
            counties={counties}
          />
        )
        break
      }
    }
  }

  return (
    <Flex
      sx={{
        height: "100%",
        flex: "1 1 auto",
        flexDirection: "column",
      }}
    >
      <Flex
        sx={{
          height: "100%",
          flex: "1 1 auto",
          overflowY: "hidden",
          position: "relative",
        }}
      >
        <Flex
          sx={{
            display: content === null ? "none !important" : "flex",
            height: "100%",
            bg: "#FFF",
            zIndex: 1000,
            flexGrow: 1,
            flexShrink: 0,
            flexBasis: layout.sidebar.width,
            flexDirection: "column",
            overflowX: "hidden",
            overflowY: "hidden",
            borderRightColor: layout.sidebar.borderRightColor,
            borderRightWidth: layout.sidebar.borderRightWidth,
            borderRightStyle: "solid",
          }}
        >
          {!isMobile && (
            <Box sx={{ flex: "0 0 auto" }}>
              {selectedUnit !== null && (
                <DesktopSelectedUnitHeader
                  name={selectedUnit.name}
                  acres={selectedUnit.acres}
                  onClose={deselectUnit}
                />
              )}
              <DesktopTabs
                tab={tab}
                hasSelectedUnit={selectedUnit !== null}
                onChange={handleTabChange}
              />
            </Box>
          )}

          <Box
            ref={contentNode}
            sx={{
              height: "100%",
              overflowY: "auto",
            }}
          >
            {content}
          </Box>
        </Flex>

        <Map
          isVisible={isMobile ? tab === "map" || tab === "unit-map" : true}
        />
      </Flex>

      {/* Mobile footer tabs */}
      {isMobile && (
        <Box
          sx={{
            flex: "0 0 auto",
            borderTop: "1px solid",
            borderTopColor: "grey.9",
          }}
        >
          <MobileTabs
            tab={tab}
            hasSelectedUnit={selectedUnit !== null}
            onChange={handleTabChange}
          />
        </Box>
      )}
    </Flex>
  )
}

export default MapContainer
