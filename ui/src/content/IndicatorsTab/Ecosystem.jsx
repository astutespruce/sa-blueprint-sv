import React from "react"
import PropTypes from "prop-types"
import { Box, Flex, Text } from "theme-ui"
import { lighten } from "@theme-ui/color"

import theme from "theme"
import EcosystemHeader from "./EcosystemHeader"
import IndicatorChart from "./IndicatorChart"

const Ecosystem = ({ id, label, acres, indicators, analysisArea }) => {
  return (
    <Box
      sx={{
        "&:not(:first-of-type)": {
          mt: "1rem",
          "&>div:first-child": {
            borderTop: "1px solid",
            borderTopColor: "blue.2",
          },
        },
      }}
    >
      <EcosystemHeader
        id={id}
        label={label}
        percent={analysisArea && acres ? (100 * acres) / analysisArea : 0}
      />
      {indicators.map(({ id: indicatorId, label, domain }) => (
        <Box
          key={indicatorId}
          sx={{
            cursor: "pointer",
            p: "1rem",
            "&:hover": {
              bg: lighten(theme.colors.blue[0], 0.01),
            },
          }}
        >
          <Text sx={{ fontSize: 2, fontWeight: "bold" }}>{label}</Text>
          {/* TODO: zonal mean from data */}
          <IndicatorChart value={domain[0]} domain={domain} />
        </Box>
      ))}
    </Box>
  )
}

export const EcosystemPropType = {
  id: PropTypes.string.isRequired,
  label: PropTypes.string.isRequired,
  acres: PropTypes.number, // missing for regional ecosystems
  indicators: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string.isRequired,
      label: PropTypes.string.isRequired,
      acres: PropTypes.arrayOf(PropTypes.number).isRequired,
      totalAcres: PropTypes.number.isRequired,
      caption: PropTypes.string.isRequired,
      description: PropTypes.string.isRequired,
      datasetID: PropTypes.string.isRequired,
      goodThreshold: PropTypes.number,
      units: PropTypes.string,
      domain: PropTypes.arrayOf(PropTypes.number).isRequired,
      values: PropTypes.arrayOf(
        PropTypes.shape({
          value: PropTypes.number.isRequired,
          label: PropTypes.string.isRequired,
        })
      ).isRequired,
    })
  ).isRequired,
}

Ecosystem.propTypes = {
  analysisArea: PropTypes.number.isRequired,
  ...EcosystemPropType,
}

export default Ecosystem
