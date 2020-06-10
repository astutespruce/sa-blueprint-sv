import React, { useState, useCallback } from "react"
import PropTypes from "prop-types"

import { Box, Flex } from "theme-ui"

import { indexBy, flatten } from "util/data"

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
  const indicators = flatten(
    Object.values(ecosystems).map(({ indicators }) => indicators)
  )
  const indicatorIndex = indexBy(indicators, "id")

  const handleClick = useCallback(id => {
    setEcosystemId(id)
  }, [])

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
          <Ecosystem
            onSelectIndicator={handleSelectIndicator}
            analysisAcres={analysisAcres}
            {...ecosystemIndex[ecosystemId]}
          />
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
