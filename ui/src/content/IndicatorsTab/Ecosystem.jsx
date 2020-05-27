import React, { useCallback } from "react"
import PropTypes from "prop-types"
import { Box, Flex, Text } from "theme-ui"

import theme from "theme"
import EcosystemHeader from "./EcosystemHeader"
import IndicatorAverageChart from "./IndicatorAverageChart"

import { IndicatorPropType } from "./IndicatorDetails"

const Ecosystem = ({
  id,
  label,
  acres,
  indicators,
  analysisAcres,
  onSelectIndicator,
}) => {
  const handleIndicatorClick = useCallback(
    indicator => () => onSelectIndicator(indicator),
    []
  )

  return (
    <Box
      sx={{
        "&:not(:first-of-type)": {
          mt: "2rem",
          "&>div:first-child": {
            borderTop: "1px solid",
            borderTopColor: "blue.3",
          },
        },
      }}
    >
      <EcosystemHeader
        id={id}
        label={label}
        percent={analysisAcres && acres ? (100 * acres) / analysisAcres : 0}
      />
      {indicators.map(indicator => (
        <Box
          key={indicator.id}
          onClick={handleIndicatorClick(indicator)}
          sx={{
            cursor: "pointer",
            px: "1rem",
            pt: "1rem",
            pb: "1.5rem",
            "&:hover": {
              bg: "blue.0",
            },
          }}
        >
          <Text sx={{ fontSize: 2, fontWeight: "bold" }}>
            {indicator.label}
          </Text>
          {/* TODO: zonal mean from data */}
          <IndicatorAverageChart
            value={
              Math.floor(
                Math.random() * (indicator.domain[1] - indicator.domain[0])
              ) + indicator.domain[0]
            }
            domain={indicator.domain}
          />
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
      ...IndicatorPropType,
    })
  ).isRequired,
}

Ecosystem.propTypes = {
  analysisAcres: PropTypes.number.isRequired,
  onSelectIndicator: PropTypes.func.isRequired,
  ...EcosystemPropType,
}

export default Ecosystem
