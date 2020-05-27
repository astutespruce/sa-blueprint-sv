import React from "react"
import PropTypes from "prop-types"

import { Box, Flex, Text } from "theme-ui"

import IndicatorPercentChart from "./IndicatorPercentChart"

const IndicatorPercentTable = ({ values, goodThreshold }) => {
  if (goodThreshold === null) {
    return (
      <Box sx={{ my: "2rem" }}>
        {values.map(({ value, label, percent, isHighValue, isLowValue }) => (
          <Flex key={value} sx={{ "&:not(:first-of-type)": { mt: "1rem" } }}>
            <Text
              sx={{
                flex: "0 0 auto",
                width: "4em",
                fontWeight: "bold",
                fontSize: [0],
              }}
            >
              {isHighValue && "High:"}
              {isLowValue && "Low:"}
            </Text>
            <IndicatorPercentChart
              value={value}
              label={label}
              percent={percent}
            />
          </Flex>
        ))}
      </Box>
    )
  }

  return <Box sx={{ my: "1rem" }}>TODO: good threshold table</Box>
}

IndicatorPercentTable.propTypes = {
  values: PropTypes.arrayOf(
    PropTypes.shape({
      value: PropTypes.number, // if null, is remainder "not evaluated" value
      label: PropTypes.string.isRequired,
      percent: PropTypes.number.isRequired,
      isHighValue: PropTypes.bool,
      isLowValue: PropTypes.bool,
    })
  ).isRequired,
  goodThreshold: PropTypes.number,
}

IndicatorPercentTable.defaultProps = {
  goodThreshold: null,
}

export default IndicatorPercentTable
