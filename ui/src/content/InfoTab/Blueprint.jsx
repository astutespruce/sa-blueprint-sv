import React from "react"
import { useStaticQuery, graphql } from "gatsby"
import { Box, Flex, Heading, Text } from "theme-ui"

import { extractNodes } from "util/graphql"

const Blueprint = () => {
  const query = useStaticQuery(graphql`
    query {
      allBlueprintJson(filter: { label: { ne: "Not a priority" } }) {
        edges {
          node {
            color
            label
            description
            area
          }
        }
      }
    }
  `).allBlueprintJson

  // sort from highest to lowest
  const priorities = extractNodes(query).reverse()

  return (
    <Box as="section" sx={{ mt: "2rem" }}>
      <Heading as="h3">Blueprint Priorities</Heading>

      {priorities.map(({ color, label, description, area }) => (
        <Box key={label}>
          <Flex
            sx={{
              justifyContent: "space-between",
              alignItems: "center",
              color: label === "Medium priority" ? "#000" : "#FFF",
              my: "0.5rem",
              p: "0.5rem",
              bg: color,
            }}
          >
            <Text as="div" sx={{ fontWeight: "bold" }}>
              {label}
            </Text>

            <Text as="div" sx={{ fontSize: [1, 0, 1], textAlign: "right" }}>
              {area} of South Atlantic
            </Text>
          </Flex>

          <Text as="p" sx={{ mb: "2rem" }}>
            {description}
          </Text>
        </Box>
      ))}
    </Box>
  )
}

export default Blueprint
