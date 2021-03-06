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

const IndicatorPixelValueChart = ({ pixelValue, values, goodThreshold }) => {
  const [currentValue] = values.filter(({ value: v }) => v === pixelValue)
  const present = currentValue !== undefined

  return (
    <Box sx={{ mt: goodThreshold ? '1.5rem' : '0.25rem' }}>
      <Flex sx={{ alignItems: 'center', opacity: present ? 1 : 0.25 }}>
        <Text sx={labelCSS}>Low</Text>
        <Flex
          sx={{
            alignItems: 'center',
            flex: '1 1 auto',
            mx: '1rem',
            border: '1px solid',
            borderColor: present ? 'grey.6' : 'grey.4',
          }}
        >
          {/* always have a 0 value bin */}
          {values[0].value > 0 ? <Box sx={patchCSS} /> : null}

          {values.map(({ value }) => (
            <React.Fragment key={value}>
              <Box sx={value === pixelValue ? currentPatchCSS : patchCSS}>
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
                      borderLeft: '0.5rem solid transparent',
                      borderRight: '0.5rem solid transparent',
                    }}
                  />
                ) : null}
              </Box>
            </React.Fragment>
          ))}
        </Flex>
        <Text sx={labelCSS}>High</Text>
      </Flex>

      <Text sx={{ color: 'grey.7', fontSize: 0, mt: '1rem' }}>
        Value: {present ? currentValue.label : 'Not present'}
      </Text>
    </Box>
  )
}

IndicatorPixelValueChart.propTypes = {
  pixelValue: PropTypes.number,
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
  pixelValue: null,
}

export default IndicatorPixelValueChart
