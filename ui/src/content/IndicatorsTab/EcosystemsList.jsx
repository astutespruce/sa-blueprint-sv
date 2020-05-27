import React, { useState, useCallback, useEffect } from "react"
import PropTypes from "prop-types"
import { Box } from "theme-ui"

import Ecosystem, { EcosystemPropType } from "./Ecosystem"

const EcosystemsList = ({ analysisArea, ecosystems }) => {
  const [{ curIndex, ecosystemID, selectedIndicator }, setState] = useState({
    ecosystemID: null,
    indicator: null,
  })

  // TODO: state management functions

  return (
    <>
      {ecosystems.map(ecosystem => (
        <Ecosystem
          key={ecosystem.id}
          analysisArea={analysisArea}
          {...ecosystem}
        />
      ))}
    </>
  )
}

EcosystemsList.propTypes = {
  analysisArea: PropTypes.number.isRequired,
  ecosystems: PropTypes.arrayOf(
    PropTypes.shape({
      ...EcosystemPropType,
    })
  ).isRequired,
}

export default EcosystemsList
