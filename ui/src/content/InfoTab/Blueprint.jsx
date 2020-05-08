import React from "react"
import { useStaticQuery, graphql } from "gatsby"
import { Box, Flex, Heading, Text } from "theme-ui"

import { extractNodes } from "util/graphql"

const Blueprint = () => {
  const query = useStaticQuery(graphql`
    query {
      allBlueprintJson(
        filter: { value: { gt: 0 } }
        sort: { fields: value, order: DESC }
      ) {
        edges {
          node {
            color
            label
            percent
            description
          }
        }
      }
    }
  `).allBlueprintJson

  const priorities = extractNodes(query)

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
              flexWrap: "wrap",
              mb: "0.5rem",
            }}
          >
            <Flex
              sx={{ alignItems: "center", width: ["100%", "100%", "auto"] }}
            >
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
              sx={{
                fontSize: [0, 0, 1],
                color: "grey.8",
                textAlign: ["left", "left", "right"],
                ml: ["2rem", "2rem", 0],
              }}
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
