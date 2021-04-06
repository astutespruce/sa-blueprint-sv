import React from 'react'
import PropTypes from 'prop-types'

import { useIndicators } from 'components/data'
import { indexBy, sum } from 'util/data'

import EcosystemList from './EcosystemList'

const IndicatorsTab = ({
  type,
  indicators: rawIndicators,
  analysisAcres,
  blueprintAcres,
}) => {
  const { ecosystems: ECOSYSTEMS, indicators: INDICATORS } = useIndicators()

  let indicators = []
  if (type === 'pixel') {
    // filter indicators that are not present or have 0 values that don't have
    // corresponding label (effectively NODATA)
    indicators = INDICATORS.map((indicator) => {
      // absent
      if (
        rawIndicators[indicator.id] === undefined ||
        rawIndicators[indicator.id] < indicator.values[0].value
      ) {
        return {
          ...indicator,
          total: 0,
        }
      }

      const pixelValue = rawIndicators[indicator.id]
      const values = indicator.values.map((value) => ({
        ...value,
        // percent is used for indicator details view
        percent: value.value === pixelValue ? 100 : 0,
      }))

      return {
        ...indicator,
        values,
        pixelValue,
        total: 100, // hardcode to 100%
      }
    })
  } else {
    // retrieve indicator results by original index
    indicators = INDICATORS.map((indicator, i) => ({
      ...indicator,
      index: i,
    })).map(({ index, ...indicator }) => {
      // absent
      if (!rawIndicators[index]) {
        return {
          ...indicator,
          index,
          values,
          total: 0,
        }
      }

      const { percent } = rawIndicators[index]

      const values = indicator.values.map(({ value, ...rest }) => ({
        value,
        ...rest,
        percent: percent[value],
      }))

      return {
        ...indicator,
        index,
        values,
        total: sum(values.map(({ percent: p }) => p)),
      }
    })
  }

  // includes indicators that may be present in coastal areas
  const hasMarine =
    indicators.filter(({ id, total }) => id.startsWith('marine_') && total > 0)
      .length > 0

  if (!hasMarine) {
    // has no marine, likely inland, don't show any marine indicators
    indicators = indicators.filter(({ id }) => !id.startsWith('marine_'))
  } else if (type === 'marine lease block') {
    // has no inland
    indicators = indicators.filter(({ id }) => id.startsWith('marine_'))
  } else if (type === 'pixel') {
    const definitelyMarine =
      indicators.filter(({ id, total }) => id === 'marine_mammals' && total > 0)
        .length > 0

    if (definitelyMarine) {
      // has no inland
      indicators = indicators.filter(({ id }) => id.startsWith('marine_'))
    }
  }

  indicators = indexBy(indicators, 'id')

  const ecosystemsPresent = new Set(
    Object.keys(indicators).map((id) => id.split('_')[0])
  )

  // Aggregate ecosystems and indicators into a nested data structure
  // ONLY for ecosystems that have indicators present
  const ecosystems = ECOSYSTEMS.filter(({ id }) =>
    ecosystemsPresent.has(id)
  ).map(
    ({
      id: ecosystemId,
      label,
      color,
      borderColor,
      indicators: ecosystemIndicators,
      ...rest
    }) => {
      const indicatorsPresent = ecosystemIndicators
        .map((indicatorId) => `${ecosystemId}_${indicatorId}`)
        .filter((indicatorId) => indicators[indicatorId])

      return {
        ...rest,
        id: ecosystemId,
        label,
        color,
        borderColor,
        indicators: indicatorsPresent.map((indicatorId) => ({
          ...indicators[indicatorId],
          ecosystem: {
            id: ecosystemId,
            label,
            color,
            borderColor,
          },
        })),
      }
    }
  )

  return (
    <EcosystemList
      type={type}
      ecosystems={ecosystems}
      analysisAcres={analysisAcres}
      blueprintAcres={blueprintAcres}
    />
  )
}

IndicatorsTab.propTypes = {
  type: PropTypes.string.isRequired,
  analysisAcres: PropTypes.number,
  blueprintAcres: PropTypes.number,

  indicators: PropTypes.oneOfType([
    // if pixel
    PropTypes.objectOf(PropTypes.number),
    // if summary unit
    // NOTE: indicators for summary units are keyed by index not id
    PropTypes.objectOf(
      PropTypes.shape({
        percent: PropTypes.arrayOf(PropTypes.number),
      })
    ),
  ]).isRequired,
}

IndicatorsTab.defaultProps = {
  analysisAcres: 0,
  blueprintAcres: 0,
}

export default IndicatorsTab
