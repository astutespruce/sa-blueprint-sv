import React, { useCallback } from 'react'
import PropTypes from 'prop-types'
import { Box, Flex, Text } from 'theme-ui'
import { lighten } from '@theme-ui/color'

import { useBreakpoints } from 'components/layout'

import IndicatorPixelValueChart from './IndicatorPixelValueChart'
import { IndicatorPropType } from './proptypes'

const PixelIndicatorListItem = ({ indicator, onSelect }) => {
  const { label, pixelValue, values, goodThreshold } = indicator

  const breakpoint = useBreakpoints()
  const isMobile = breakpoint === 0

  const handleClick = useCallback(() => {
    onSelect(indicator)
  }, [indicator, onSelect])

  const present = indicator.total > 0

  if (!present) {
    return (
      <Flex
        sx={{
          alignItems: 'baseline',
          justifyContent: 'space-between',
          px: '1rem',
          py: '0.25rem',
          color: 'grey.7',
          cursor: 'default',
          '&:not(:first-of-type)': {
            borderTop: '2px solid',
            borderTopColor: 'grey.1',
          },
        }}
      >
        <Text
          sx={{
            flex: '1 1 auto',
            fontSize: 2,
          }}
        >
          {label}
        </Text>
        <Text sx={{ flex: '0 0 auto', fontSize: '10px' }}>(absent)</Text>
      </Flex>
    )
  }

  return (
    <Box
      onClick={handleClick}
      sx={{
        cursor: 'pointer',
        px: '1rem',
        pt: '1rem',
        pb: '2.5rem',
        position: 'relative',
        '&:hover': {
          bg: lighten('grey.0', 0.01),
          '& label': {
            display: 'block',
          },
        },
        '&:not(:first-of-type)': {
          borderTop: '2px solid',
          borderTopColor: 'grey.1',
        },
      }}
    >
      <Text
        sx={{
          color: 'primary',
          fontSize: 2,
          fontWeight: 'bold',
        }}
      >
        {label}
      </Text>

      <IndicatorPixelValueChart
        pixelValue={pixelValue}
        values={values}
        goodThreshold={goodThreshold}
      />
      <Text
        as="label"
        sx={{
          color: 'primary',
          fontSize: 'small',
          textAlign: 'center',
          position: 'absolute',
          bottom: 0,
          left: 0,
          right: 0,
          display: 'none',
        }}
      >
        {isMobile ? 'tap' : 'click'} for more details
      </Text>
    </Box>
  )
}

PixelIndicatorListItem.propTypes = {
  indicator: PropTypes.shape(IndicatorPropType).isRequired,
  onSelect: PropTypes.func.isRequired,
}

export default PixelIndicatorListItem
