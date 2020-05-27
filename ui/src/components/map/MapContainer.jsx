import React, { useState, useCallback, useRef, useEffect } from "react"
import { Box, Button, Text, Flex, useThemeUI } from "theme-ui"

import { useBreakpoints } from "components/layout"
import {
  InfoTab,
  ContactTab,
  FindLocationTab,
  PrioritiesTab,
  IndicatorsTab,
  ThreatsTab,
  PartnersTab,
} from "content"
import {
  SelectedUnitHeader as MobileSelectedUnitHeader,
  Tabs as MobileTabs,
} from "components/layout/mobile"

import {
  SelectedUnitHeader as DesktopSelectedUnitHeader,
  Tabs as DesktopTabs,
} from "components/layout/desktop"

import { sum } from "util/data"

// TODO: remove
import { inlandUnit as demoUnit } from "test/exampleUnits"

import Map from "./Map"

const MapContainer = () => {
  const {
    theme: { layout },
  } = useThemeUI()

  // flag so we only do some things on initial loading
  const isDuringLoad = useRef(true)

  const breakpoint = useBreakpoints()
  const isMobile = breakpoint === 0

  const [{ tab, selectedUnit }, setState] = useState({
    tab: breakpoint === 0 ? "map" : "info",
    selectedUnit: null,
  })

  useEffect(() => {
    isDuringLoad.current = false
  }, [])

  // handle window resize from mobile to desktop, so that we show content again
  // if map tab previously selected
  useEffect(() => {
    if (breakpoint > 0 && !isDuringLoad) {
      const nextTab = tab === "map" ? "info" : "unit-priorities"
      setState(prevState => ({ ...prevState, tab: nextTab }))
    }
  }, [breakpoint])

  const handleTabChange = useCallback(tab => {
    setState(prevState => ({
      ...prevState,
      tab,
    }))
  })
  const selectUnit = useCallback(unit => {
    setState(({ tab: prevTab, ...prevState }) => {
      let nextTab = prevTab
      if (prevTab === "map") {
        nextTab = "unit-map"
      } else if (!prevTab.startsWith("unit-")) {
        nextTab = "unit-priorities"
      }
      return {
        ...prevState,
        selectedUnit: unit,
        tab: nextTab,
      }
    })
  }, [])

  const deselectUnit = useCallback(() => {
    setState(({ tab: prevTab, ...prevState }) => ({
      ...prevState,
      selectedUnit: null,
      tab: prevTab === "unit-map" || isMobile ? "map" : "info",
    }))
  }, [])

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
      blueprint,
      blueprint_total: blueprintAcres,
      corridors,
      corridors_total: corridorAcres,
      ecosystems: ecosystemAcres,
      indicators,
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
            corridorAcres={corridorAcres}
          />
        )
        break
      }
      case "unit-indicators": {
        const indicatorArea = indicators.map(indicatorId => ({
          id: indicatorId,
          acres: selectedUnit[indicatorId],
          totalAcres: sum(selectedUnit[indicatorId]),
        }))
        content = (
          <IndicatorsTab
            unitType={unitType}
            analysisAcres={blueprintAcres}
            ecosystemAcres={ecosystemAcres}
            indicatorAcres={indicatorArea}
          />
        )
        break
      }
      case "unit-threats": {
        //   TODO: props
        content = <ThreatsTab />
        break
      }
      case "unit-partners": {
        //   TODO: props
        content = <PartnersTab />
        break
      }
    }
  }

  console.log("selected unit", selectedUnit, "tab", tab)

  return (
    <Flex
      sx={{
        height: "100%",
        flexDirection: "column",
      }}
    >
      {/* Mobile header for selected unit */}
      {isMobile && selectedUnit !== null && (
        <MobileSelectedUnitHeader
          name={selectedUnit.name}
          onClose={deselectUnit}
        />
      )}
      <Flex
        sx={{
          height: "100%",
          flex: "1 1 auto",
          overflowY: "hidden",
        }}
      >
        <Flex
          sx={{
            display: content === null ? "none" : "block",
            height: "100%",
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
            sx={{
              height: "100%",
              overflowY: "auto",
            }}
          >
            {content}
          </Box>
        </Flex>

        {/* Map placeholder */}
        <Box
          onClick={() => selectUnit(demoUnit)}
          sx={{
            background: "linear-gradient(0deg, #08AEEA 0%, #2AF598 100%)",
            flex: "1 1 auto",
            width: "100%",
          }}
        />
        {/* <Map /> */}
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
