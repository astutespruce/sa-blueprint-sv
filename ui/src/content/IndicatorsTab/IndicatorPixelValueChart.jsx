import React from 'react'
import PropTypes from 'prop-types'
import { Box, Flex, Text } from 'theme-ui'

const labelCSS = {
  color: 'grey.6',
  fontSize: 0,
  flex: '0 0 auto',
}

const patchCSS = {
  position: 'relative',
  flex: '1 1 auto',
  height: '0.75rem',
  bg: 'grey.0',
  '&:not(:first-of-type)': {
    borderLeft: '1px solid',
    borderLeftColor: 'grey.3',
  },
}

const currentPatchCSS = {
  ...patchCSS,
  bg: 'grey.6',
}

const goodPatchCSS = {
  ...patchCSS,
  bg: '#5fb785',
}

const notGoodPatchCSS = {
  ...patchCSS,
  bg: '#e77778',
}

const getPatchCSS = (value, isCurrent, goodThreshold) => {
  if (goodThreshold !== null) {
    return value >= goodThreshold ? goodPatchCSS : notGoodPatchCSS
  }
  return isCurrent ? currentPatchCSS : patchCSS
}

const IndicatorPixelValueChart = ({ pixelValue, values, goodThreshold }) => {
  const [currentValue] = values.filter(({ value: v }) => v === pixelValue)

  return (
    <Box sx={{ mt: '1.5rem' }}>
      <Flex sx={{ alignItems: 'center' }}>
        <Text sx={labelCSS}>Low</Text>
        <Flex
          sx={{
            alignItems: 'center',
            flex: '1 1 auto',
            mx: '1rem',
            border: '1px solid',
            borderColor: 'grey.6',
          }}
        >
          {/* always have a 0 value bin */}
          {values[0].value > 0 ? (
            <Box sx={getPatchCSS(0, false, goodThreshold)} />
          ) : null}

          {values.map(({ value }) => (
            <React.Fragment key={value}>
              <Box sx={getPatchCSS(value, value === pixelValue, goodThreshold)}>
                {value === goodThreshold ? (
                  <Text
                    sx={{
                      position: 'absolute',
                      width: '94px',
                      top: '-1.2rem',
                      color: 'grey.6',
                      fontSize: '10px',
                      borderLeft: '1px dashed',
                      borderLeftColor: 'grey.6',
                    }}
                  >
                    &rarr; good condition
                  </Text>
                ) : null}
                {value === pixelValue ? (
                  <Box
                    sx={{
                      position: 'absolute',
                      left: '50%',
                      top: '0.8rem',
                      ml: '-0.25rem',
                      borderBottom: '0.6rem solid',
                      borderBottomColor: 'grey.9',
                      borderLeft: '0.5rem solid #FFF',
                      borderRight: '0.5rem solid #FFF',
                    }}
                  />
                ) : null}
              </Box>
            </React.Fragment>
          ))}
        </Flex>
        <Text sx={labelCSS}>High</Text>
      </Flex>

      {currentValue ? (
        <Text sx={{ color: 'grey.6', fontSize: 1, mt: '1rem' }}>
          Value: {currentValue.label}
        </Text>
      ) : null}
    </Box>
  )
}

IndicatorPixelValueChart.propTypes = {
  pixelValue: PropTypes.number.isRequired,
  values: PropTypes.arrayOf(
    PropTypes.shape({
      value: PropTypes.number.isRequired,
      label: PropTypes.string.isRequired,
    })
  ).isRequired,
  goodThreshold: PropTypes.number,
}

IndicatorPixelValueChart.defaultProps = {
  goodThreshold: null,
}

export default IndicatorPixelValueChart
