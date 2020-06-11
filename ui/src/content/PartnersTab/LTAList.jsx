import React from "react"
import PropTypes from "prop-types"
import { Box } from "theme-ui"

import { OutboundLink } from "components/link"

const LTAList = ({ counties }) => {
  return (
    <Box as="ul">
      {counties.map(({ FIPS, state, county }) => (
        <li key={FIPS}>
          <OutboundLink to={`http://findalandtrust.org/counties/${FIPS}`}>
            {county}, {state}
          </OutboundLink>
        </li>
      ))}
    </Box>
  )
}

LTAList.propTypes = {
  counties: PropTypes.arrayOf(
    PropTypes.shape({
      FIPS: PropTypes.string.isRequired,
      state: PropTypes.string.isRequired,
      county: PropTypes.string.isRequired,
    })
  ),
}

export default LTAList
