import React, { useState, useCallback, useEffect } from "react"
import PropTypes from "prop-types"

import { indexBy, flatten } from "util/data"

import Ecosystem, { EcosystemPropType } from "./Ecosystem"
import IndicatorDetails from "./IndicatorDetails"

const DesktopEcosystemList = ({ analysisAcres, ecosystems }) => {
  const indicators = flatten(
    Object.values(ecosystems).map(({ indicators }) => indicators)
  )

  const [selectedIndicator, setSelectedIndicator] = useState(null)

  const handleSelectIndicator = useCallback(indicator => {
    console.log("select indicator", indicator)
    setSelectedIndicator(indicator)
  }, [])

  const handleCloseIndicator = useCallback(() => setSelectedIndicator(null), [])

  return (
    <>
      {selectedIndicator ? (
        <IndicatorDetails
          onClose={handleCloseIndicator}
          {...selectedIndicator}
        />
      ) : (
        ecosystems.map(ecosystem => (
          <Ecosystem
            key={ecosystem.id}
            onSelectIndicator={handleSelectIndicator}
            analysisAcres={analysisAcres}
            {...ecosystem}
          />
        ))
      )}
    </>
  )
}

DesktopEcosystemList.propTypes = {
  analysisAcres: PropTypes.number.isRequired,
  ecosystems: PropTypes.arrayOf(
    PropTypes.shape({
      ...EcosystemPropType,
    })
  ).isRequired,
}

export default DesktopEcosystemList
