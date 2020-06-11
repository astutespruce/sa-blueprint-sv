import React from "react"
import PropTypes from "prop-types"
import { graphql, useStaticQuery } from "gatsby"
import { PieChart } from "react-minimal-pie-chart"
import { Box, Flex, Divider, Heading, Text } from "theme-ui"

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
      color: "#ffebc2",
      label: "Not a hub or corridor",
    })
  }

  const index = 0
  const selected = 0

  return (
    <Box sx={{ py: "1.5rem", pl: "1rem", pr: "2rem" }}>
      <Box as="section">
        <Heading as="h4">Blueprint 2.x Priority</Heading>
        <Text sx={{ color: "grey.7" }}>for shared conservation action</Text>

        <Flex sx={{ alignItems: "center", mt: "2rem" }}>
          <PieChart
            data={blueprintChartData}
            segmentsShift={1}
            lineWidth={80}
            radius={chartWidth / 4 - 2}
            style={{
              width: chartWidth,
              flex: "0 1 auto",
              //   background: "#333",
              //   borderRadius: "100em",
            }}
          />

          <PieChartLegend elements={blueprintChartData} />
        </Flex>
      </Box>

      {corridorChartData.length > 0 ? (
        <>
          <Divider variant="styles.hr.light" sx={{ my: "3rem" }} />
          <Box as="section">
            <Heading as="h4">Hubs &amp; Corridors</Heading>

            <Flex sx={{ alignItems: "center", mt: "2rem" }}>
              <PieChart
                data={corridorChartData}
                segmentsShift={1}
                lineWidth={80}
                radius={chartWidth / 4 - 2}
                style={{
                  width: chartWidth,
                  flex: "0 1 auto",
                  // background: "#333",
                  // borderRadius: "100em",
                }}
              />

              <PieChartLegend elements={corridorChartData} />
            </Flex>
          </Box>
        </>
      ) : (
        <Text sx={{ textAlign: "center", color: "grey.6" }}>
          No hubs or corridors in this area.
        </Text>
      )}
    </Box>
  )
}

PrioritiesTab.propTypes = {
  blueprint: PropTypes.arrayOf(PropTypes.number).isRequired,
  blueprintAcres: PropTypes.number.isRequired,
  corridors: PropTypes.arrayOf(PropTypes.number).isRequired,
  corridorAcres: PropTypes.number.isRequired,
}

export default PrioritiesTab
