import React from "react"
import PropTypes from "prop-types"
import { Flex, Box, Text, Progress } from "theme-ui"

import { formatPercent } from "util/format"

const IndicatorPercentChart = ({ value, label, percent, isGood }) => {
  let color = null
  if (value === null) {
    color = "grey.7"
  } else if (isGood) {
    color = "rgb(95, 183, 133)"
  } else if (isGood === false) {
    color = "rgb(231, 119, 120)"
  }

  console.log("set color", value, color)

  // let variant = 'default'
  // if (isGood) {
  //     variant = 'green'
  // }

  return (
    <Box sx={{ flex: "1 1 auto" }}>
      <Flex sx={{ justifyContent: "space-between", fontSize: 0 }}>
        <Text sx={{ flex: "1 1 auto" }}>{label}</Text>
        <Text sx={{ color: "grey.6", flex: "0 0 auto", ml: "1em" }}>
          {formatPercent(percent)}%
        </Text>
      </Flex>
      <Progress value={percent} max={100} color={color} />
    </Box>
  )
}

IndicatorPercentChart.propTypes = {
  value: PropTypes.string, // if null, is remainder value
  label: PropTypes.string.isRequired,
  percent: PropTypes.number.isRequired,
  isGood: PropTypes.bool, // true, false, null=not defined for this indicator
}

IndicatorPercentChart.defaultProps = {
  value: null,
  isGood: null,
}

export default IndicatorPercentChart
