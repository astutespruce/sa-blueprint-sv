import React from "react"
import PropTypes from "prop-types"
import { graphql, useStaticQuery } from "gatsby"
import { PieChart } from "react-minimal-pie-chart"
import { Box, Flex, Divider, Heading, Text } from "theme-ui"

import { PieChartLegend } from "components/chart"

import { extractNodes } from "util/graphql"
import { sum } from "util/data"

const PrioritiesTab = ({ blueprint, corridors }) => {
  const query = useStaticQuery(graphql`
    query {
      allBlueprintJson(sort: { fields: value, order: ASC }) {
        edges {
          node {
            color
            label
          }
        }
      }
      allCorridorsJson(sort: { fields: value, order: ASC }) {
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

  console.log("corridor categories", corridorCategories, corridors)

  const chartWidth = 200

  const blueprintChartData = blueprint
    .slice()
    .map((percent, i) => ({
      value: percent,
      ...priorityCategories[i],
    }))
    .filter(({ value }) => value > 0)
    .reverse()

  const corridorChartData = corridors
    .slice()

    .map((percent, i) => ({
      value: percent,
      ...corridorCategories[i],
    }))
    .filter(({ value }) => value > 0)
    .reverse()

  const corridorsTotal = sum(corridors)

  if (corridorsTotal < 100) {
    corridorChartData.push({
      value: 100 - corridorsTotal,
      color: "#ffebc2",
      label: "Not a hub or corridor",
    })
  }

  return (
    <Box sx={{ py: "2rem", pl: "1rem", pr: "2rem" }}>
      <Box as="section">
        <Heading as="h3">Blueprint 2020 Priority</Heading>
        <Text sx={{ color: "grey.7" }}>for shared conservation action</Text>

        <Flex sx={{ alignItems: "center", mt: "2rem" }}>
          <PieChart
            data={blueprintChartData}
            lineWidth={60}
            radius={chartWidth / 4 - 2}
            style={{
              width: chartWidth,
              flex: "0 1 auto",
            }}
          />

          <PieChartLegend elements={blueprintChartData} />
        </Flex>
      </Box>

      {corridorChartData.length > 0 ? (
        <>
          <Divider variant="styles.hr.light" sx={{ my: "3rem" }} />
          <Box as="section">
            <Heading as="h3">Hubs &amp; Corridors</Heading>

            <Flex sx={{ alignItems: "center", mt: "2rem" }}>
              <PieChart
                data={corridorChartData}
                lineWidth={60}
                radius={chartWidth / 4 - 2}
                style={{
                  width: chartWidth,
                  flex: "0 1 auto",
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
  blueprint: PropTypes.arrayOf(PropTypes.number),
  corridors: PropTypes.arrayOf(PropTypes.number),
}

PrioritiesTab.defaultProps = {
  blueprint: [],
  corridors: [],
}

export default PrioritiesTab
