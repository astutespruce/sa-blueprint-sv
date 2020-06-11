import React from "react"
import PropTypes from "prop-types"

import { Box, Text, Divider } from "theme-ui"

import SLR from "./SLR"
import Urban from "./Urban"

const ThreatsTab = ({ unitType, slr, slrAcres, urban, urbanAcres }) => {
  if (unitType !== "subwatershed") {
    return (
      <Text sx={{ color: "grey.7" }}>
        No information on threats is available for marine units.
      </Text>
    )
  }

  const hasSLR = slr && slr.length > 0

  return (
    <Box sx={{ py: "1.5rem", pl: "1rem", pr: "2rem" }}>
      {slr && slr.length > 0 ? (
        <Box as="section">
          <SLR percents={slr} />
        </Box>
      ) : (
        <Text sx={{ color: "grey.7" }}>
          This watershed is not impacted by up to 6 feet of projected sea level
          rise.
        </Text>
      )}

      {urban && urban.length > 0 ? (
        <>
          {hasSLR ? (
            <Divider variant="styles.hr.light" sx={{ my: "3rem" }} />
          ) : null}
          <Box as="section">
            <Urban percents={urban} />
          </Box>
        </>
      ) : (
        <Text sx={{ color: "grey.7" }}>
          This watershed is not impacted by projected urbanization up to 2100.
        </Text>
      )}
    </Box>
  )
}

ThreatsTab.propTypes = {
  unitType: PropTypes.string.isRequired,
  slr: PropTypes.arrayOf(PropTypes.number).isRequired,
  slrAcres: PropTypes.number.isRequired,
  urban: PropTypes.arrayOf(PropTypes.number).isRequired,
  urbanAcres: PropTypes.number.isRequired,
}

export default ThreatsTab
