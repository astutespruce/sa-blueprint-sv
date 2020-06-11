import React from "react"
import PropTypes from "prop-types"

import { Box, Text } from "theme-ui"

import { LineChart } from "components/chart"
import { OutboundLink } from "components/link"

// Actual urban in 2009, then projected from 2020 onward
// shifted to 2010 for even scale
const LEVELS = [2010, 2020, 2030, 2040, 2050, 2060, 2070, 2080, 2090, 2100]

const Urban = ({ percents }) => {
  return (
    <>
      <Text sx={{ color: "grey.7" }}>
        Extent of current and projected urbanization within this subwatershed:
      </Text>
      <Box sx={{ position: "relative", mt: "2rem" }}>
        <Text
          sx={{
            fontSize: 1,
            color: "grey.7",
            position: "absolute",
            transform: "rotate(180deg)",
            writingMode: "vertical-lr",
            height: "100%",
            textAlign: "center",
          }}
        >
          Percent of area
        </Text>

        <Box
          sx={{
            ml: "1.5rem",
            mb: "1rem",
            height: "200px",
            "& text": {
              fontSize: 0,
              fill: "grey.7",
            },
          }}
        >
          <LineChart
            areaColor="#D90000"
            areaVisible
            gridVisible={false}
            pathWidth={2}
            pathColor="#D90000"
            pointsColor="#D90000"
            pointsStrokeWidth={0}
            labelsStepX={20}
            labelsFormatX={x => x || ""}
            data={percents.map((y, i) => ({ x: LEVELS[i], y }))}
          />
        </Box>

        <Text sx={{ fontSize: 1, color: "grey.7", textAlign: "center" }}>
          Decade
        </Text>
      </Box>

      <Text sx={{ mt: "2rem", color: "grey.7", fontSize: 1 }}>
        Current (2009) urban extent estimated using the{" "}
        <OutboundLink to="https://www.mrlc.gov/data">
          National Land Cover Database
        </OutboundLink>
        . Projected urban extent from 2020 onward were derived from the{" "}
        <OutboundLink to="http://www.basic.ncsu.edu/dsl/urb.html">
          SLEUTH urban growth model
        </OutboundLink>
        .
      </Text>
    </>
  )
}

Urban.propTypes = {
  percents: PropTypes.arrayOf(PropTypes.number).isRequired,
}

export default Urban
