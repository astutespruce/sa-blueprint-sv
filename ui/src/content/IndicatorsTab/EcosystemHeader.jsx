import React from "react"
import PropTypes from "prop-types"

import { Box, Flex, Heading, Image, Text } from "theme-ui"
import { darken } from "@theme-ui/color"

const EcosystemHeader = ({
  id,
  label,
  group: { id: groupId, label: groupLabel, color, borderColor },
}) => {
  const icon = require(`images/${id}.svg`)

  return (
    <Flex
      sx={{
        alignItems: "center",
        justifyContent: "space-between",
        bg: color,
        py: ["1rem", "0.5rem"],
        px: "1rem",
        borderBottom: "1px solid",
        borderBottomColor: borderColor,
      }}
    >
      <Flex sx={{ alignItems: "center" }}>
        <Image
          src={icon}
          sx={{
            width: "2.5em",
            height: "2.5em",
            mr: "0.5em",
            bg: "#FFF",
            borderRadius: "2.5em",
          }}
        />
        <Box>
          {groupId === "marine" ? null : (
            <Text sx={{ fontSize: 0, color: "grey.8" }}>{groupLabel}</Text>
          )}
          <Heading as="h4">{label}</Heading>
        </Box>
      </Flex>
    </Flex>
  )
}

EcosystemHeader.propTypes = {
  id: PropTypes.string.isRequired,
  label: PropTypes.string.isRequired,
  group: PropTypes.shape({
    id: PropTypes.string.isRequired,
    label: PropTypes.string.isRequired,
    color: PropTypes.string.isRequired,
  }),
}

export default EcosystemHeader
