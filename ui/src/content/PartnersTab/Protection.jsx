import React from "react"
import PropTypes from "prop-types"
import { graphql, useStaticQuery } from "gatsby"
import { Box, Flex, Text } from "theme-ui"

import { PercentBarChart } from "components/chart"
import { OutboundLink } from "components/link"
import { extractNodes } from "util/graphql"
import { sortByFunc, sum } from "util/data"

const Protection = ({ analysisAcres, protectionAcres }) => {
  const query = useStaticQuery(graphql`
    query {
      allProtectionJson(sort: { fields: value, order: DESC }) {
        edges {
          node {
            id: value
            label
            color
          }
        }
      }
    }
  `).allProtectionJson

  const categories = extractNodes(query)

  const bars = categories
    .filter(({ id }) => protectionAcres[id])
    .map(category => ({
      ...category,
      percent: (100 * protectionAcres[category.id]) / analysisAcres,
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
        Land protection status is derived from the TNC{" "}
        <OutboundLink to="https://www.conservationgateway.org/ConservationByGeography/NorthAmerica/UnitedStates/edc/reportsdata/terrestrial/secured/Pages/default.aspx">
          Secured Lands Database
        </OutboundLink>{" "}
        (2018 Edition).
      </Text>
    </>
  )
}

Protection.propTypes = {
  analysisAcres: PropTypes.number.isRequired,
  protectionAcres: PropTypes.objectOf(PropTypes.number),
}

export default Protection
