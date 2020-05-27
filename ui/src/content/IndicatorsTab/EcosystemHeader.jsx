import React from "react"
import PropTypes from "prop-types"

import { Box, Flex, Heading, Text, Image } from "theme-ui"

import { formatPercent } from "util/format"

const EcosystemHeader = ({ id, label, percent, isFirst }) => {
  const icon = require(`images/${id}.svg`)

  //   const topBorder = isFirst
  //     ? {}
  //     : {
  //         borderTop: "1px solid",
  //         borderTopColor: "blue.2",
  //       }

  return (
    <Flex
      sx={{
        alignItems: "center",
        justifyContent: "space-between",
        bg: "blue.0",
        height: "4rem",
        px: "1rem",
        borderBottom: "1px solid",
        borderBottomColor: "blue.2",
        // ...topBorder,
      }}
    >
      <Flex sx={{ alignItems: "center" }}>
        <Image
          src={icon}
          sx={{ width: "2.5em", height: "2.5em", mr: "0.5em" }}
        />
        <Heading as="h4">{label}</Heading>
      </Flex>
      {percent > 0 && (
        <Box sx={{ color: "grey.7", fontSize: 0, textAlign: "right" }}>
          <b>{formatPercent(percent)}%</b>
          <br />
          of area
        </Box>
      )}
    </Flex>
  )
}

EcosystemHeader.propTypes = {
  id: PropTypes.string.isRequired,
  label: PropTypes.string.isRequired,
  percent: PropTypes.number,
}

EcosystemHeader.defaultProps = {
  percent: null, // some ecosystems don't have a percent
}

export default EcosystemHeader