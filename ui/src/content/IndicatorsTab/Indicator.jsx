import React, { useCallback, useState } from "react"
import PropTypes from "prop-types"
import { Flex, Box, Text } from "theme-ui"
import { lighten } from "@theme-ui/color"

import { useBreakpoints } from "components/layout"
import { formatPercent } from "util/format"

import IndicatorAverageChart from "./IndicatorAverageChart"
import { IndicatorPropType } from "./proptypes"

const Indicator = ({ indicator, onSelect }) => {
  const { id, label, avg, total, domain } = indicator

  const breakpoint = useBreakpoints()
  const isMobile = breakpoint === 0

  const [isHover, setIsHover] = useState(false)

  const handleClick = useCallback(() => {
    onSelect(indicator)
  }, [indicator, onSelect])

  const handleMouseEnter = useCallback(() => {
    setIsHover(() => true)
  })

  const handleMouseLeave = useCallback(() => {
    setIsHover(() => false)
  })

  return (
    <Box
      onClick={handleClick}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      sx={{
        cursor: "pointer",
        px: "1rem",
        pt: "1rem",
        pb: "2.5rem",
        position: "relative",
        "&:hover": {
          bg: lighten("grey.0", 0.01),
        },
        "&:not(:first-of-type)": {
          borderTop: "2px solid",
          borderTopColor: "grey.1",
        },
      }}
    >
      <Flex
        sx={{
          justifyContent: "space-between",
          alignItems: "flex-end",
        }}
      >
        <Text
          sx={{
            color: "primary",
            fontSize: 2,
            fontWeight: "bold",
          }}
        >
          {label}
        </Text>

        <Text
          sx={{
            fontSize: 0,
            borderRadius: "1em",
            bg: "grey.1",
            px: "0.5em",
            py: "0.25em",
          }}
        >
          {formatPercent(total)}% of area
        </Text>
      </Flex>

      <Text
        sx={{
          fontSize: 0,
          color: "grey.7",
          visibility: isHover ? "visible" : "hidden",
        }}
      >
        Average value in this area:
      </Text>

      <IndicatorAverageChart value={avg} domain={domain} highlight={isHover} />

      <Text
        sx={{
          color: "primary",
          fontSize: "small",
          textAlign: "center",
          position: "absolute",
          bottom: 0,
          left: 0,
          right: 0,
          display: isHover ? "block" : "none",
        }}
      >
        {isMobile ? "tap" : "click"} for more details
      </Text>
    </Box>
  )
}

Indicator.propTypes = {
  indicator: PropTypes.shape(IndicatorPropType),
  onSelect: PropTypes.func.isRequired,
}

export default Indicator
