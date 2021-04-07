import React, { useState, useCallback, memo } from 'react'
import PropTypes from 'prop-types'
import { dequal as deepEqual } from 'dequal'

import { useMapData } from 'components/data'
import { flatten, indexBy } from 'util/data'
import { useIsEqualEffect } from 'util/hooks'

import Ecosystem from './Ecosystem'
import IndicatorDetails from './IndicatorDetails'
import { EcosystemPropType } from './proptypes'

const EcosystemList = ({ type, ecosystems, analysisAcres, blueprintAcres }) => {
  const { selectedIndicator, setSelectedIndicator } = useMapData()
  const indicators = flatten(
    Object.values(ecosystems).map(({ indicators: i }) => i)
  )
  const indicatorsIndex = indexBy(indicators, 'id')

  useIsEqualEffect(() => {
    if (!selectedIndicator) {
      return
    }

    if (!indicatorsIndex[selectedIndicator]) {
      // reset selected indicator, it isn't present in this set (outside valid ecosystems)
      setSelectedIndicator(null)
    }
  }, [indicators, selectedIndicator])

  const handleSelectIndicator = useCallback(
    (indicator) => {
      setSelectedIndicator(indicator.id)
    },
    [setSelectedIndicator]
  )

  const handleCloseIndicator = useCallback(() => setSelectedIndicator(null), [
    setSelectedIndicator,
  ])

  return (
    <>
      {selectedIndicator && indicatorsIndex[selectedIndicator] ? (
        <IndicatorDetails
          type={type}
          analysisAcres={analysisAcres}
          blueprintAcres={blueprintAcres}
          onClose={handleCloseIndicator}
          {...indicatorsIndex[selectedIndicator]}
        />
      ) : (
        ecosystems.map((ecosystem) => (
          <Ecosystem
            key={ecosystem.id}
            type={type}
            onSelectIndicator={handleSelectIndicator}
            {...ecosystem}
          />
        ))
      )}
    </>
  )
}

EcosystemList.propTypes = {
  type: PropTypes.string.isRequired,
  analysisAcres: PropTypes.number.isRequired,
  blueprintAcres: PropTypes.number.isRequired,
  ecosystems: PropTypes.arrayOf(PropTypes.shape(EcosystemPropType)).isRequired,
}

export default memo(EcosystemList, (prev, next) => deepEqual(prev, next))
