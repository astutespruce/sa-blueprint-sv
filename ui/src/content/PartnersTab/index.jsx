import React from "react"
import PropTypes from "prop-types"

import { Box, Divider, Heading, Text } from "theme-ui"

import Ownership from "./Ownership"
import Protection from "./Protection"
import LTAList from "./LTAList"

const PartnersTab = ({
  unitType,
  analysisAcres,
  ownershipAcres,
  protectionAcres,
  counties,
}) => {
  if (unitType !== "subwatershed") {
    return (
      <Box sx={{ py: "2rem", pl: "1rem", pr: "2rem" }}>
        <Text sx={{ color: "grey.7" }}>
          No information on ownership or protection status is available for
          marine units.
        </Text>
      </Box>
    )
  }

  return (
    <Box sx={{ py: "2rem", pl: "1rem", pr: "2rem" }}>
      <Box as="section">
        <Heading as="h3">Conserved Lands Ownership</Heading>
        {ownershipAcres === null ? (
          <Text sx={{ color: "grey.7" }}>No information available.</Text>
        ) : (
          <Ownership
            analysisAcres={analysisAcres}
            ownershipAcres={ownershipAcres}
          />
        )}
      </Box>

      <Divider variant="styles.hr.light" sx={{ my: "3rem" }} />

      <Box as="section">
        <Heading as="h3">Land Protection Status</Heading>
        {protectionAcres === null ? (
          <Text sx={{ color: "grey.7" }}>No information available.</Text>
        ) : (
          <Protection
            analysisAcres={analysisAcres}
            protectionAcres={protectionAcres}
          />
        )}
      </Box>

      <Divider variant="styles.hr.light" sx={{ my: "3rem" }} />

      <Box as="section">
        <Heading as="h3">Land Trusts by County</Heading>
        {counties === null ? (
          <Text sx={{ color: "grey.7" }}>No information available.</Text>
        ) : (
          <LTAList counties={counties} />
        )}
      </Box>
    </Box>
  )
}

PartnersTab.propTypes = {
  unitType: PropTypes.string.isRequired,
  analysisAcres: PropTypes.number.isRequired,
  ownershipAcres: PropTypes.objectOf(PropTypes.number),
  protectionAcres: PropTypes.objectOf(PropTypes.number),
  counties: PropTypes.arrayOf(
    PropTypes.shape({
      FIPS: PropTypes.string.isRequired,
      state: PropTypes.string.isRequired,
      county: PropTypes.string.isRequired,
    })
  ),
}

PartnersTab.defaultProps = {
  ownershipAcres: null,
  protectionAcres: null,
  counties: null,
}

export default PartnersTab
