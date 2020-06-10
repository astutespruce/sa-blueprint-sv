import React, { useState, useCallback } from "react"
import PropTypes from "prop-types"

import { Box, Flex } from "theme-ui"

import { SwipeContainer } from "components/layout"
import { indexBy } from "util/data"

import Ecosystem, { EcosystemPropType } from "./Ecosystem"
import EcosystemNav from "./EcosystemNav"
import IndicatorDetails from "./IndicatorDetails"

const MobileEcosystemList = ({ analysisAcres, ecosystems }) => {
  const [ecosystemId, setEcosystemId] = useState(ecosystems[0].id)
  const [selectedIndicator, setSelectedIndicator] = useState(null)

  const handleSelectIndicator = useCallback(indicator => {
    console.log("select indicator", indicator)
    setSelectedIndicator(indicator)
  }, [])

  const handleCloseIndicator = useCallback(() => setSelectedIndicator(null), [])

  const ecosystemIndex = indexBy(ecosystems, "id")

  const handleClick = useCallback(id => {
    setEcosystemId(id)
  }, [])

  const handleSwipeMove = args => {
    console.log("onSwipeMove", args)
  }

  const handleSwipeEnd = args => {
    console.log("onSwipeEnd", args)
  }

  return (
    <Flex
      sx={{
        height: "100%",
        overflowY: "auto",
        flexDirection: "column",
        flex: "1 1 auto",
      }}
    >
      <Box sx={{ flex: "1 1 auto" }}>
        {selectedIndicator ? (
          <IndicatorDetails
            onClose={handleCloseIndicator}
            {...selectedIndicator}
          />
        ) : (
          <SwipeContainer
            onSwipeMove={handleSwipeMove}
            onSwipeEnd={handleSwipeEnd}
          >
            {/* <Ecosystem
              onSelectIndicator={handleSelectIndicator}
              analysisAcres={analysisAcres}
              {...ecosystemIndex[ecosystemId]}
            /> */}
            {ecosystems.map(ecosystem => (
              <Ecosystem
                key={ecosystem.id}
                onSelectIndicator={handleSelectIndicator}
                analysisAcres={analysisAcres}
                {...ecosystem}
              />
            ))}
          </SwipeContainer>
        )}
      </Box>
      <Box
        sx={{ flex: "0 0 auto", display: selectedIndicator ? "none" : "block" }}
      >
        <EcosystemNav
          ecosystemId={ecosystemId}
          ecosystems={ecosystems}
          onClick={handleClick}
        />
      </Box>
    </Flex>
  )
}

MobileEcosystemList.propTypes = {
  analysisAcres: PropTypes.number.isRequired,
  ecosystems: PropTypes.arrayOf(
    PropTypes.shape({
      ...EcosystemPropType,
    })
  ).isRequired,
}

export default MobileEcosystemList
