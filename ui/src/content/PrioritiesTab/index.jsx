import React from "react"
import PropTypes from "prop-types"
import { graphql, useStaticQuery } from "gatsby"
import { PieChart } from "react-minimal-pie-chart"
import { Box, Flex, Heading, Text } from "theme-ui"

import { PieChartLegend } from "components/chart"

import { extractNodes } from "util/graphql"

const PrioritiesTab = ({
  blueprint,
  blueprintAcres,
  corridors,
  corridorAcres,
}) => {
  const query = useStaticQuery(graphql`
    query {
      allBlueprintJson(sort: { fields: value, order: DESC }) {
        edges {
          node {
            color
            label
          }
        }
      }
      allCorridorsJson(sort: { order: ASC, fields: value }) {
        edges {
          node {
            label
            color
          }
        }
      }
    }
  `)

  const priorityCategories = extractNodes(query.allBlueprintJson)
  const corridorCategories = extractNodes(query.allCorridorsJson)

  const chartWidth = 200

  const blueprintChartData = blueprint
    .slice()
    .reverse()
    .map((acres, i) => ({
      value: (100 * acres) / blueprintAcres,
      ...priorityCategories[i],
    }))
    .filter(({ value }) => value > 0)

  const corridorChartData = corridors
    .slice()
    .reverse()
    .map((acres, i) => ({
      value: (100 * acres) / blueprintAcres,
      ...corridorCategories[i],
    }))
    .filter(({ value }) => value > 0)

  if (corridorAcres < blueprintAcres) {
    corridorChartData.push({
      value: (100 * (blueprintAcres - corridorAcres)) / blueprintAcres,
      color: "#F6F6F6",
      label: "Not a hub or corridor",
    })
  }

  //   const corridorSum = corridorChartData.reduce((sum, v) => sum + v, 0)
  //   if (corridorSum > 0 && corridorSum < 100) {

  //   }

  return (
    <>
      <Box as="section">
        <Heading as="h3">Blueprint 2.x Priority</Heading>
        <Text sx={{ color: "grey.7" }}>for shared conservation action</Text>

        <Flex sx={{ alignItems: "center", mt: "2rem" }}>
          <PieChart
            data={blueprintChartData}
            style={{ width: chartWidth, flex: "1 1 auto" }}
          />

          <PieChartLegend elements={blueprintChartData} />
        </Flex>
      </Box>

      {corridorChartData.length > 0 ? (
        <Box as="section" sx={{ mt: "4rem" }}>
          <Heading as="h3">Hubs &amp; Corridors</Heading>

          <Flex sx={{ alignItems: "center", mt: "2rem" }}>
            <PieChart
              data={corridorChartData}
              style={{ width: chartWidth, flex: "1 1 auto" }}
            />

            <PieChartLegend elements={corridorChartData} />
          </Flex>
        </Box>
      ) : (
        <Text sx={{ textAlign: "center", color: "grey.6" }}>
          No hubs or corridors in this area.
        </Text>
      )}
    </>
  )
}

PrioritiesTab.propTypes = {
  blueprint: PropTypes.arrayOf(PropTypes.number).isRequired,
  blueprintAcres: PropTypes.number.isRequired,
  corridors: PropTypes.arrayOf(PropTypes.number).isRequired,
  corridorAcres: PropTypes.number.isRequired,
}

export default PrioritiesTab
