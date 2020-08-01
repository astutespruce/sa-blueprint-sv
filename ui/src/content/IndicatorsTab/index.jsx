import React from "react"
import PropTypes from "prop-types"
import { graphql, useStaticQuery } from "gatsby"

import { useBreakpoints } from "components/layout"
import { indexBy, sortByFunc } from "util/data"
import { extractNodes } from "util/graphql"

import DesktopEcosystemList from "./DesktopEcosystemList"
import MobileEcosystemList from "./MobileEcosystemList"

// TODO: split between mobile swiper and list view here, let each manage own state?

const IndicatorsTab = ({ unitType, analysisAcres, indicatorAcres }) => {
  const breakpoint = useBreakpoints()
  const isMobile = breakpoint === 0

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

  const ecosystemsPresent = new Set(
    Object.keys(indicatorAcres).map(id => id.split("_")[0])
  )
  console.log("ecosystems present", ecosystemsPresent, ECOSYSTEMS)

  const indicatorsIndex = indexBy(extractNodes(query.indicators), "id")

  // Aggregate ecosystems and indicators into a nested data structure
  // ONLY for ecosystems that have indicators present

  const ecosystems = extractNodes(
    query.ecosystems.filter(({ id }) => ecosystemsPresent.has(id))
  ).map(
    ({ id: ecosystemId, label, color, borderColor, indicators, ...rest }) => {
      const indicatorsPresent = indicators
        .map(indicatorId => `${ecosystemId}_${indicatorId}`)
        .filter(indicatorId => indicatorAcres[indicatorId])

      return {
        ...rest,
        id: ecosystemId,
        indicators: indicatorsPresent.map(indicatorId => ({
          ...indicatorsIndex[indicatorId],
          ...indicatorAcres[indicatorId],
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

  //   if (isMobile) {
  //     return (
  //       <MobileEcosystemList
  //         analysisAcres={analysisAcres}
  //         ecosystems={ecosystems}
  //       />
  //     )
  //   }

  return (
    <DesktopEcosystemList
      ecosystems={ecosystems}
      analysisAcres={analysisAcres}
    />
  )
}

IndicatorsTab.propTypes = {
  unitType: PropTypes.string.isRequired,
  analysisAcres: PropTypes.number.isRequired,
  indicatorAcres: PropTypes.objectOf(
    PropTypes.shape({
      id: PropTypes.string.isRequired,
      acres: PropTypes.arrayOf(PropTypes.number).isRequired,
      totalAcres: PropTypes.number.isRequired,
    })
  ).isRequired,
}

export default IndicatorsTab
