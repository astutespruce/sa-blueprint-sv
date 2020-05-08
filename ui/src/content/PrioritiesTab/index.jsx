import React from "react"
import PropTypes from "prop-types"
import { graphql, useStaticQuery } from "gatsby"
import { PieChart } from "react-minimal-pie-chart"
import { Box, Flex, Heading, Text } from "theme-ui"

import { formatPercent } from "util/format"
import { extractNodes } from "util/graphql"

const PrioritiesTab = ({ blueprint, totalAcres }) => {
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
    }
  `).allBlueprintJson

  const priorities = extractNodes(query)

  const chartData = blueprint
    .slice()
    .reverse()
    .map((acres, i) => ({
      value: (100 * acres) / totalAcres,
      ...priorities[i],
    }))
    .filter(({ value }) => value > 0)

  console.log("blueprint percents", chartData)

  return (
    <Box as="section">
      <Heading as="h3">Blueprint 2.x Priority</Heading>
      <Text sx={{ color: "grey.7" }}>for shared conservation action</Text>

      <Flex sx={{ alignItems: "center", mt: "2rem" }}>
        <PieChart data={chartData} style={{ width: 200, flex: "1 1 auto" }} />
        <Box sx={{ ml: "2rem", minWidth: "140px" }}>
          {chartData.map(({ color, value, label }) => (
            <Flex
              key={label}
              sx={{
                align: "center",
                mb: "0.5rem",
                fontSize: [0],
              }}
            >
              <Box
                sx={{
                  width: "1.5em",
                  height: "1.5em",
                  mr: "0.5rem",
                  flex: "0 0 auto",
                }}
                style={{ backgroundColor: color }}
              />
              <Flex sx={{ flexWrap: "wrap" }}>
                <Text sx={{ mr: "0.5em" }}>{label}</Text>
                <Text sx={{ color: "grey.6", flex: "0 0 auto" }}>
                  ({formatPercent(value)}%)
                </Text>
              </Flex>
            </Flex>
          ))}
        </Box>
      </Flex>
    </Box>
  )
}

PrioritiesTab.propTypes = {
  blueprint: PropTypes.arrayOf(PropTypes.number).isRequired,
  totalAcres: PropTypes.number.isRequired,
}

export default PrioritiesTab
