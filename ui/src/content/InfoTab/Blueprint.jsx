import React from "react"
import { useStaticQuery, graphql } from "gatsby"
import { Box, Flex, Heading, Text } from "theme-ui"

import { PercentDonut } from "components/chart"
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
            percent
          }
        }
      }
    }
  `).allBlueprintJson

  // sort from highest priority to lowest
  const priorities = extractNodes(query).reverse()

  return (
    <Box as="section" sx={{ mt: "2rem" }}>
      <Heading as="h3" sx={{ mb: "0.5rem" }}>
        Blueprint Priorities
      </Heading>

      {priorities.map(({ color, label, description, percent }) => (
        <Box key={label}>
          <Flex
            sx={{
              justifyContent: "space-between",
              alignItems: "center",
            }}
          >
            <Flex sx={{ alignItems: "center" }}>
              <Box
                sx={{
                  width: "1.5rem",
                  height: "1.5rem",
                  borderRadius: "1rem",
                  bg: color,
                  mr: "0.5rem",
                  flex: "0 0 auto",
                }}
              />
              <Text as="div" sx={{ fontWeight: "bold" }}>
                {label}
              </Text>
            </Flex>
            <Text
              as="div"
              sx={{ fontSize: [1, 0, 1], color: "grey.8", textAlign: "right" }}
            >
              {percent}% of South Atlantic
            </Text>
          </Flex>

          <Text as="p" sx={{ fontSize: [2, 1, 2], mb: "2rem", ml: "2rem" }}>
            {description}
          </Text>
        </Box>
      ))}
    </Box>
  )
}

export default Blueprint
