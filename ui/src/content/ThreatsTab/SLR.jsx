import React from "react"
import PropTypes from "prop-types"

import { Box, Text, Heading } from "theme-ui"

import { OutboundLink } from "components/link"
import { LineChart } from "components/chart"

// SLR levels are in feet above current mean sea level: 0...6

const SLR = ({ percents }) => {
  return (
    <>
      <Heading as="h4">Sea Level Rise</Heading>
      <Box
        sx={{
          position: "relative",
          mt: "2rem",
        }}
      >
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
            areaColor="#004da8"
            areaVisible
            gridVisible={false}
            pathWidth={2}
            pathColor="#004da8"
            pointsColor="#004da8"
            pointsStrokeWidth={0}
            labelsStepX={1}
            labelsFormatX={x => x}
            data={percents.map((y, i) => ({ x: i, y }))}
          />
        </Box>

        <Text
          sx={{ fontSize: 1, color: "grey.7", textAlign: "center" }}
          className="text-center text-quiet text-smaller chart-line-x-axis-label"
        >
          Amount of sea level rise (feet)
        </Text>
      </Box>

      <Text sx={{ mt: "2rem" }}>
        Extent of inundation by projected sea level rise within this
        subwatershed. Values from the{" "}
        <OutboundLink to="https://coast.noaa.gov/digitalcoast/data/slr.html">
          NOAA sea-level rise inundation data
        </OutboundLink>
        .
      </Text>
    </>
  )
}

SLR.propTypes = {
  percents: PropTypes.arrayOf(PropTypes.number).isRequired,
}

export default SLR
