import React, { useState, useCallback, useEffect } from "react"
import PropTypes from "prop-types"

import { flatten } from "util/data"

import Ecosystem, { EcosystemPropType } from "./Ecosystem"
import IndicatorDetails from "./IndicatorDetails"

const DesktopEcosystemList = ({ ecosystems, analysisAcres }) => {
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
          analysisAcres={analysisAcres}
          onClose={handleCloseIndicator}
          {...selectedIndicator}
        />
      ) : (
        ecosystems.map(ecosystem => (
          <Ecosystem
            key={ecosystem.id}
            onSelectIndicator={handleSelectIndicator}
            {...ecosystem}
          />
        ))
      )}
    </>
  )
}

DesktopEcosystemList.propTypes = {
  ecosystems: PropTypes.arrayOf(PropTypes.shape(EcosystemPropType)).isRequired,
  analysisAcres: PropTypes.number.isRequired,
}

export default DesktopEcosystemList
