import React from "react"
import PropTypes from "prop-types"
import { Box, Flex, Text, Heading, Image } from "theme-ui"
import { Reply } from "emotion-icons/fa-solid"

import { OutboundLink } from "components/link"
import { formatPercent, formatNumber } from "util/format"
import theme from "theme"

import IndicatorPercentTable from "./IndicatorPercentTable"

const IndicatorDetails = ({
  id,
  label,
  ecosystemLabel,
  acres,
  totalAcres,
  description,
  caption,
  datasetID,
  goodThreshold,
  units,
  domain,
  values,
  analysisAcres,
  onClose,
}) => {
  const ecosystemId = id.split("_")[0]
  const icon = require(`images/${ecosystemId}.svg`)

  const percentTableValues = values
    .map(({ value, label }, i) => ({
      value,
      label,
      percent: (100 * acres[value]) / analysisAcres,
      isHighValue: i === values.length - 1,
      isLowValue: i === 0,
    }))
    .reverse()

  // remainder value for areas not analyzed for this indicator
  if (totalAcres < analysisAcres) {
    percentTableValues.push({
      value: null,
      label: "Not evaluated for this indicator",
      percent: (100 * (analysisAcres - totalAcres)) / analysisAcres,
    })
  }

  console.log("percent values", percentTableValues)

  return (
    <Flex
      sx={{
        flexDirection: "column",
        height: "100%",
        overflowY: "hidden",
      }}
    >
      <Flex
        onClick={onClose}
        sx={{
          justifyContent: "space-between",
          alignItems: "center",
          cursor: "pointer",
          bg: "blue.1",
          py: "0.5rem",
          pl: "0.25rem",
          pr: "1rem",
          borderBottom: "1px solid",
          borderBottomColor: "blue.3",
        }}
      >
        <Flex sx={{}}>
          <Reply
            css={{
              width: "0.75em",
              height: "0.75em",
              flex: "0 0 auto",
              margin: 0,
              color: theme.colors.grey[7],
            }}
          />

          <Flex sx={{ alignItems: "center" }}>
            <Image
              src={icon}
              sx={{ width: "2.5em", height: "2.5em", mr: "0.5em" }}
            />
            <Box>
              <Text sx={{ fontSize: 0 }}>{ecosystemLabel}</Text>
              <Heading as="h4">{label}</Heading>
            </Box>
          </Flex>
        </Flex>
        <Box sx={{ color: "grey.8", fontSize: 0, textAlign: "right" }}>
          <b>{formatPercent((100 * totalAcres) / analysisAcres)}%</b>
          <br />
          of area
        </Box>
      </Flex>

      <Box
        sx={{ p: "1rem", height: "100%", flex: "1 1 auto", overflowY: "auto" }}
      >
        <Text as="p">{description}</Text>

        <IndicatorPercentTable
          values={percentTableValues}
          goodThreshold={goodThreshold}
        />

        <Text as="p" sx={{ mt: "2rem", fontSize: 1 }}>
          {caption}
        </Text>
        <Box sx={{ mt: "2rem" }}>
          <OutboundLink
            to={`https://salcc.databasin.org/datasets/${datasetID}`}
          >
            View this indicator in the Conservation Planning Atlas
          </OutboundLink>
        </Box>
      </Box>
    </Flex>
  )
}

export const IndicatorPropType = {
  id: PropTypes.string.isRequired,
  label: PropTypes.string.isRequired,
  ecosystemLabel: PropTypes.string.isRequired,
  acres: PropTypes.arrayOf(PropTypes.number).isRequired,
  totalAcres: PropTypes.number.isRequired,
  analysisAcres: PropTypes.number.isRequired,
  caption: PropTypes.string.isRequired,
  description: PropTypes.string.isRequired,
  datasetID: PropTypes.string.isRequired,
  goodThreshold: PropTypes.number,
  units: PropTypes.string,
  domain: PropTypes.arrayOf(PropTypes.number).isRequired,
  values: PropTypes.arrayOf(
    PropTypes.shape({
      value: PropTypes.number.isRequired,
      label: PropTypes.string.isRequired,
    })
  ).isRequired,
}

IndicatorDetails.propTypes = {
  ...IndicatorPropType,
  onClose: PropTypes.func.isRequired,
}

export default IndicatorDetails
