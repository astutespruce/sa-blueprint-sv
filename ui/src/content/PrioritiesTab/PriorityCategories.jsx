import React from 'react'
import PropTypes from 'prop-types'
import { Box, Flex, Text } from 'theme-ui'

const defaultCSS = {
  color: 'grey.8',
  border: '1px solid transparent',
  py: '0.5rem',
  px: '1rem',
}

const activeCSS = {
  ...defaultCSS,
  borderRadius: '0.5rem',
  bg: '#FFF',
  borderColor: 'grey.2',
  boxShadow: '1px 1px 6px #dce2e3',
  color: 'text',
}

const PriorityCategories = ({ categories, value: currentValue }) => (
  <Box sx={{ fontSize: 1, pt: '0.5rem' }}>
    {categories.map(({ value, label, color, description, description2 }) => (
      <Box key={value} sx={value === currentValue ? activeCSS : defaultCSS}>
        <Flex sx={{ alignItems: 'center' }}>
          <Box
            sx={{
              bg: color,
              width: '1rem',
              height: '1rem',
              border: '1px solid #CCC',
              mr: '0.5rem',
            }}
          />
          <Box
            sx={{
              fontWeight: 'bold',
              lineHeight: 1,
            }}
          >
            {label}
          </Box>
        </Flex>
        {description ? (
          <Text sx={{ fontSize: 0, ml: '1.5rem' }}>
            {description} {description2}
          </Text>
        ) : null}
      </Box>
    ))}
  </Box>
)

PriorityCategories.propTypes = {
  categories: PropTypes.arrayOf(
    PropTypes.shape({
      value: PropTypes.number.isRequired,
      label: PropTypes.string.isRequired,
      color: PropTypes.string.isRequired,
      description: PropTypes.string,
      description2: PropTypes.string,
    })
  ).isRequired,
  value: PropTypes.number,
}

PriorityCategories.defaultProps = {
  value: null,
}

export default PriorityCategories
