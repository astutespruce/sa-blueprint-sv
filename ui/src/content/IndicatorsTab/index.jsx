import React from "react"
import PropTypes from "prop-types"
import { graphql, useStaticQuery } from "gatsby"

import { indexBy, sum } from "util/data"
import { extractNodes } from "util/graphql"

import EcosystemList from "./EcosystemList"

const IndicatorsTab = ({
  unitType,
  analysisAcres,
  indicators: rawIndicators,
}) => {
  const query = useStaticQuery(graphql`
    query {
      ecosystems: allEcosystemsJson {
        edges {
          node {
            id
            label
            color
            borderColor
            indicators
          }
        }
      }
      indicators: allIndicatorsJson {
        edges {
          node {
            id
            label
            datasetID
            description
            units
            domain
            continuous
            goodThreshold
            values {
              value
              label
            }
          }
        }
      }
    }
  `)

  // retrieve indicator results by original index
  const indicators = indexBy(
    extractNodes(query.indicators)
      .map((indicator, i) => ({
        ...indicator,
        index: i,
      }))
      .filter((_, i) => rawIndicators[i] !== undefined)
      .map(({ index, ...indicator }) => {
        const { percent, avg = null } = rawIndicators[index]
        return {
          ...indicator,
          index,
          values: indicator.values.map(({ value, ...rest }) => ({
            value,
            ...rest,
            percent: percent[value],
          })),
          avg,
          total: sum(percent),
        }
      }),
    "id"
  )

  const ecosystemsPresent = new Set(
    Object.keys(indicators).map(id => id.split("_")[0])
  )

  // Aggregate ecosystems and indicators into a nested data structure
  // ONLY for ecosystems that have indicators present
  const ecosystems = extractNodes(query.ecosystems)
    .filter(({ id }) => ecosystemsPresent.has(id))
    .map(
      ({
        id: ecosystemId,
        label,
        color,
        borderColor,
        indicators: ecosystemIndicators,
        ...rest
      }) => {
        const indicatorsPresent = ecosystemIndicators
          .map(indicatorId => `${ecosystemId}_${indicatorId}`)
          .filter(indicatorId => indicators[indicatorId])

        return {
          ...rest,
          id: ecosystemId,
          label,
          color,
          borderColor,
          indicators: indicatorsPresent.map(indicatorId => ({
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

  console.log("ecosystems", ecosystems)

  return <EcosystemList ecosystems={ecosystems} />
}

IndicatorsTab.propTypes = {
  unitType: PropTypes.string.isRequired,

  // NOTE: indicators are keyed by index not id
  indicators: PropTypes.objectOf(
    PropTypes.shape({
      percent: PropTypes.arrayOf(PropTypes.number).isRequired,
      avg: PropTypes.number,
    })
  ).isRequired,
}

export default IndicatorsTab
