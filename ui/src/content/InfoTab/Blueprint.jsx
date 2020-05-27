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
            labelColor
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
      <Heading as="h3" sx={{ mb: "1rem" }}>
        Blueprint Priorities
        <Text sx={{ color: "grey.8", fontSize: 0, fontWeight: "normal" }}>
          (% of the South Atlantic)
        </Text>
      </Heading>

      {priorities.map(({ color, label, labelColor, description, percent }) => (
        <Box key={label}>
          <Box
            sx={{
              justifyContent: "space-between",
              alignItems: "center",
              flexWrap: "wrap",
              //   mb: "0.5rem",
            }}
          >
            <Flex
              sx={{ alignItems: "center", width: ["100%", "100%", "auto"] }}
            >
              <Flex
                sx={{
                  alignItems: "center",
                  justifyContent: "center",
                  width: "2.5rem",
                  height: "2.5rem",
                  borderRadius: "2rem",
                  bg: color,
                  mr: "0.5rem",
                  flex: "0 0 auto",
                }}
              >
                <Text
                  sx={{
                    color: labelColor || "#FFF",
                    fontSize: 0,
                    fontWeight: "bold",
                  }}
                >
                  {percent}%
                </Text>
              </Flex>
              <Text as="div" sx={{ fontWeight: "bold" }}>
                {label}
              </Text>
            </Flex>
            {/* <Text
              as="div"
              sx={{
                fontSize: 0,
                color: "grey.8",
                // textAlign: ["left", "left", "right"],
                // ml: ["2rem", "2rem", 0],
                ml: "2rem",
              }}
            >
              {percent}% of South Atlantic
            </Text> */}
          </Box>

          <Text
            as="p"
            sx={{ fontSize: [2, 1, 2], mb: "2rem", ml: "3rem", mt: "-0.5rem" }}
          >
            {description}
          </Text>
        </Box>
      ))}
    </Box>
  )
}

export default Blueprint
