import React from "react"
import PropTypes from "prop-types"
import { graphql, useStaticQuery } from "gatsby"
import { Box, Flex, Text } from "theme-ui"

import { PercentBarChart } from "components/chart"
import { OutboundLink } from "components/link"
import { extractNodes } from "util/graphql"
import { sortByFunc, sum } from "util/data"

const Ownership = ({ analysisAcres, ownershipAcres }) => {
  const query = useStaticQuery(graphql`
    query {
      allOwnershipJson(sort: { fields: value, order: DESC }) {
        edges {
          node {
            id: value
            label
            color
          }
        }
      }
    }
  `).allOwnershipJson

  const categories = extractNodes(query)

  const bars = categories
    .filter(({ id }) => ownershipAcres[id])
    .map(category => ({
      ...category,
      percent: (100 * ownershipAcres[category.id]) / analysisAcres,
    }))

  bars.sort(sortByFunc("percent", false))

  const remainder = 100 - sum(bars.map(({ percent }) => percent))
  if (remainder > 0) {
    bars.push({
      label: "Not conserved",
      color: "grey.5",
      percent: remainder,
    })
  }

  return (
    <>
      {bars.map(bar => (
        <PercentBarChart {...bar} sx={{ mt: "0.5rem", mb: "1rem" }} />
      ))}

      <Text sx={{ color: "grey.7", fontSize: 1 }}>
        Land ownership is derived from the TNC{" "}
        <OutboundLink to="https://www.conservationgateway.org/ConservationByGeography/NorthAmerica/UnitedStates/edc/reportsdata/terrestrial/secured/Pages/default.aspx">
          Secured Lands Database
        </OutboundLink>{" "}
        (2018 Edition).
      </Text>
    </>
  )
}

Ownership.propTypes = {
  analysisAcres: PropTypes.number.isRequired,
  ownershipAcres: PropTypes.objectOf(PropTypes.number),
}

export default Ownership
