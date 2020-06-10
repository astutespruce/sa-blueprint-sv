import React from "react"
import PropTypes from "prop-types"
import { graphql, useStaticQuery } from "gatsby"

import { useBreakpoints } from "components/layout"
import { indexBy, sortByFunc } from "util/data"
import { extractNodes } from "util/graphql"

import DesktopEcosystemList from "./DesktopEcosystemList"
import MobileEcosystemList from "./MobileEcosystemList"

// TODO: split between mobile swiper and list view here, let each manage own state?

const IndicatorsTab = ({
  unitType,
  analysisAcres,
  ecosystemAcres,
  indicatorAcres,
}) => {
  const breakpoint = useBreakpoints()
  const isMobile = breakpoint === 0

  const query = useStaticQuery(graphql`
    query {
      ecosystems: allEcosystemsJson(
        sort: { fields: value, order: ASC }
        filter: { value: { ne: null } }
      ) {
        edges {
          node {
            id
            label
            indicators
          }
        }
      }
      regionalEcosystems: allEcosystemsJson(filter: { value: { eq: null } }) {
        edges {
          node {
            id
            label
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
            caption
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

  const ECOSYSTEMS = extractNodes(query.ecosystems)
  const REGIONAL_ECOSYSTEMS = extractNodes(query.regionalEcosystems)
  const INDICATORS = indexBy(extractNodes(query.indicators), "id")

  const indicators = indexBy(indicatorAcres, "id")

  // Aggregate ecosystems and indicators into a nested data structure
  // ONLY for ecosystems that are present (acres > 0)
  const ecosystems = ECOSYSTEMS.map((values, i) => ({
    ...values,
    acres: ecosystemAcres[i],
  }))
    .filter(({ acres }) => acres > 0)
    .map(
      (
        {
          id: ecosystemId,
          label: ecosystemLabel,
          indicators: indicatorIds,
          ...rest
        },
        i
      ) => {
        const ecosystemIndicators = indicatorIds
          .map(indicatorId => {
            const id = `${ecosystemId}_${indicatorId}`
            return {
              ...INDICATORS[id],
              ...indicators[id],
              ecosystemLabel,
              analysisAcres,
            }
          })
          .sort(sortByFunc("label", true))

        return {
          id: ecosystemId,
          label: ecosystemLabel,
          ...rest,
          indicators: ecosystemIndicators,
        }
      }
    )
    .sort(sortByFunc("acres", false))

  if (unitType === "subwatershed") {
    const regionalEcosystems = REGIONAL_ECOSYSTEMS.map(
      ({
        id: ecosystemId,
        label: ecosystemLabel,
        indicators: indicatorIds,
        ...rest
      }) => {
        const ecosystemIndicators = indicatorIds
          .map(indicatorId => {
            const id = `${ecosystemId}_${indicatorId}`
            return {
              ...INDICATORS[id],
              ...indicators[id],
              ecosystemLabel,
              analysisAcres,
            }
          })
          .sort(sortByFunc("label", true))

        return {
          id: ecosystemId,
          label: ecosystemLabel,
          ...rest,
          indicators: ecosystemIndicators,
        }
      }
    )
    ecosystems.push(...regionalEcosystems)
  }

  console.log("ecosystem data aggregated", ecosystems)

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
      analysisAcres={analysisAcres}
      ecosystems={ecosystems}
    />
  )
}

IndicatorsTab.propTypes = {
  unitType: PropTypes.string.isRequired,
  analysisAcres: PropTypes.number.isRequired,
  ecosystemAcres: PropTypes.arrayOf(PropTypes.number).isRequired,
  indicatorAcres: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string.isRequired,
      acres: PropTypes.arrayOf(PropTypes.number).isRequired,
      totalAcres: PropTypes.number.isRequired,
    })
  ).isRequired,
}

export default IndicatorsTab
