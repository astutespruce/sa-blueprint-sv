import React from "react"
import PropTypes from "prop-types"
import { Box, Flex, Text, Divider } from "theme-ui"
import { ArrowUp, ArrowDown } from "emotion-icons/fa-solid"

import { sum } from "util/data"
import { formatPercent } from "util/format"

import IndicatorPercentChart from "./IndicatorPercentChart"

const labelCSS = {
  flex: "0 0 auto",
  width: "5em",
  fontWeight: "bold",
  fontSize: 0,
}

const arrowCSS = {
  margin: 0,
  flex: "0 0 auto",
  width: "1em",
  height: "1em",
}

const IndicatorPercentTable = ({ values, goodThreshold }) => {
  const remainder = values.filter(({ value }) => value === null)

  if (goodThreshold === null) {
    return (
      <Box sx={{ my: "2rem" }}>
        {values
          .filter(({ value }) => value !== null)
          .map(({ value, label, percent, isHighValue, isLowValue }) => (
            <Flex
              key={value}
              sx={{
                alignItems: isLowValue ? "flex-end" : "flex-start",
                "&:not(:first-of-type)": { mt: "1rem" },
              }}
            >
              <Text sx={labelCSS}>
                {isHighValue && (
                  <Flex sx={{ alignItems: "center" }}>
                    <ArrowUp css={arrowCSS} />
                    <Text sx={{ ml: "0.1rem" }}>High:</Text>
                  </Flex>
                )}
                {isLowValue && (
                  <Flex sx={{ alignItems: "center" }}>
                    <ArrowDown css={arrowCSS} />
                    <Text sx={{ ml: "0.1rem" }}>Low:</Text>
                  </Flex>
                )}
              </Text>
              <IndicatorPercentChart
                value={value}
                label={label}
                percent={percent}
              />
            </Flex>
          ))}

        {remainder.length > 0 ? (
          <>
            <Divider variant="styles.hr.dashed" />
            <Box>
              <Flex>
                <Text sx={labelCSS}>The rest:</Text>
                <IndicatorPercentChart {...remainder[0]} />
              </Flex>
            </Box>
          </>
        ) : null}
      </Box>
    )
  }

  const goodPercents = values.filter(
    ({ value }) => value !== null && value >= goodThreshold
  )
  const notGoodPercents = values.filter(
    ({ value }) => value !== null && value < goodThreshold
  )

  const totalGoodPercent = sum(goodPercents.map(({ percent }) => percent))
  const totalNotGoodPercent = sum(notGoodPercents.map(({ percent }) => percent))

  return (
    <Box sx={{ my: "2rem" }}>
      {goodPercents.map(({ value, label, percent, isHighValue }) => (
        <Flex key={value} sx={{ "&:not(:first-of-type)": { mt: "1rem" } }}>
          <Text sx={labelCSS}>
            {isHighValue && (
              <Flex sx={{ alignItems: "center" }}>
                <ArrowUp css={arrowCSS} />
                <Text sx={{ ml: "0.1rem" }}>High:</Text>
              </Flex>
            )}
          </Text>
          <IndicatorPercentChart
            value={value}
            label={label}
            percent={percent}
            isGood={true}
          />
        </Flex>
      ))}

      <Box sx={{ mt: "1.5rem", color: "grey.7", fontSize: 0 }}>
        <Flex sx={{ justifyContent: "center", alignItems: "center" }}>
          <ArrowUp css={arrowCSS} />
          <Text sx={{ width: "14em", ml: "0.1em" }}>
            {formatPercent(totalGoodPercent)}% in good condition
          </Text>
        </Flex>

        <Box
          sx={{
            borderBottom: "1px dashed",
            borderBottomColor: "grey.6",
            height: "1px",
            my: "0.25rem",
          }}
        />

        <Flex sx={{ justifyContent: "center", alignItems: "center" }}>
          <ArrowDown css={arrowCSS} />
          <Text sx={{ width: "14em", ml: "0.1em" }}>
            {formatPercent(totalNotGoodPercent)}% not in good condition
          </Text>
        </Flex>
      </Box>

      {notGoodPercents.map(({ value, label, percent, isLowValue }) => (
        <Flex key={value} sx={{ mt: "1rem", alignItems: "flex-end" }}>
          <Text sx={labelCSS}>
            {isLowValue && (
              <Flex sx={{ alignItems: "center" }}>
                <ArrowDown css={arrowCSS} />
                <Text sx={{ ml: "0.1rem" }}>Low:</Text>
              </Flex>
            )}
          </Text>
          <IndicatorPercentChart
            value={value}
            label={label}
            percent={percent}
            isGood={false}
          />
        </Flex>
      ))}

      {remainder.length > 0 ? (
        <>
          <Divider variant="styles.hr.dashed" />
          <Box>
            <Flex>
              <Text sx={labelCSS}>The rest:</Text>
              <IndicatorPercentChart {...remainder[0]} />
            </Flex>
          </Box>
        </>
      ) : null}
    </Box>
  )
}

IndicatorPercentTable.propTypes = {
  values: PropTypes.arrayOf(
    PropTypes.shape({
      value: PropTypes.number, // if null, is remainder "not evaluated" value
      label: PropTypes.string.isRequired,
      percent: PropTypes.number.isRequired,
      isHighValue: PropTypes.bool,
      isLowValue: PropTypes.bool,
    })
  ).isRequired,
  goodThreshold: PropTypes.number,
}

IndicatorPercentTable.defaultProps = {
  goodThreshold: null,
}

export default IndicatorPercentTable
