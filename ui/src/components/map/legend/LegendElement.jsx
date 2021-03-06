import React, { memo } from 'react'
import PropTypes from 'prop-types'
import { Flex, Box, Text } from 'theme-ui'

const LegendElement = ({ label, type, color, outlineColor, outlineWidth }) => (
  <Flex
    sx={{
      alignItems: 'flex-start',
      lineHeight: 1,
    }}
  >
    {type === 'fill' && (
      <Box
        sx={{
          flex: '0 0 auto',
          width: '1.25em',
          height: '1em',
          borderRadius: '0.25em',
          mr: '0.5rem',
          bg: color,
          border: outlineWidth !== 0 ? `${outlineWidth}px solid` : 'none',
          borderColor: outlineColor,
        }}
      />
    )}
    <Text>{label}</Text>
  </Flex>
)

LegendElement.propTypes = {
  label: PropTypes.string.isRequired,
  type: PropTypes.string,
  color: PropTypes.oneOfType([PropTypes.string, PropTypes.func]).isRequired,
  outlineColor: PropTypes.oneOfType([PropTypes.string, PropTypes.func]),
  outlineWidth: PropTypes.number,
}

LegendElement.defaultProps = {
  type: 'fill',
  outlineColor: null,
  outlineWidth: 0,
}

export default memo(LegendElement, () => true)
