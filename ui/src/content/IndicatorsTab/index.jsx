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
      ecosystemGroups: allEcosystemGroupsJson {
        edges {
          node {
            id
            label
            color
            borderColor
            ecosystems
          }
        }
      }
      ecosystems: allEcosystemsJson {
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

  console.log("indicatorArea", indicatorAcres)

  const ECOSYSTEM_GROUPS = extractNodes(query.ecosystemGroups)
  const ECOSYSTEMS = indexBy(extractNodes(query.ecosystems), "id")
  const INDICATORS = indexBy(extractNodes(query.indicators), "id")

  console.log("ecosystems list", extractNodes(query.ecosystems))

  const ecosystemsPresent = new Set(
    Object.keys(indicatorAcres).map(id => id.split("_")[0])
  )
  console.log("ecosystems present", ecosystemsPresent, ECOSYSTEMS)

  // Aggregate ecosystems and indicators into a nested data structure
  // ONLY for ecosystems that have indicators present
  // Output this as a flattened list of ecosystems in order of groups
  const ecosystems = []

  ECOSYSTEM_GROUPS.forEach(
    ({
      id: groupId,
      label,
      color,
      borderColor,
      ecosystems: groupEcosystemIds,
    }) => {
      const ids = groupEcosystemIds.filter(e => ecosystemsPresent.has(e))

      console.log("ids present", ids)

      if (ids.length > 0) {
        const groupEcosystems = ids
          .map(ecosystemId => {
            const indicatorsPresent = ECOSYSTEMS[ecosystemId].indicators
              .map(indicatorId => `${ecosystemId}_${indicatorId}`)
              .filter(indicatorId => indicatorAcres[indicatorId])

            const group = {
              id: groupId,
              label,
              color,
              borderColor,
            }

            return {
              group,
              ...ECOSYSTEMS[ecosystemId],
              indicators: indicatorsPresent.map(indicatorId => ({
                ...INDICATORS[indicatorId],
                ...indicatorAcres[indicatorId],
                ecosystem: {
                  id: ecosystemId,
                  label: ECOSYSTEMS[ecosystemId].label,
                  group,
                },
              })),
            }
          })
          .filter(({ indicators }) => indicators.length > 0)

        if (groupEcosystems.length > 0) {
          ecosystems.push(...groupEcosystems)
        }
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
