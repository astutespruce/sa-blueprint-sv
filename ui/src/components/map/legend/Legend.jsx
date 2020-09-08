import React from 'react'
import PropTypes from 'prop-types'
import { Box, Text } from 'theme-ui'

import LegendElement from './LegendElement'

const Legend = ({ label, elements }) => {
  return (
    <Box>
      {label ? (
        <Text sx={{ lineHeight: 1, fontWeight: 'bold', fontSize: 1 }}>
          {label}
        </Text>
      ) : null}
      {elements.map((element) => (
        <Box
          key={element.label}
          sx={{
            '&:not(:first-of-type)': {
              mt: '0.5rem',
            },
          }}
        >
          <LegendElement {...element} />
        </Box>
      ))}
    </Box>
  )
}
Legend.propTypes = {
  label: PropTypes.string,
  elements: PropTypes.arrayOf(PropTypes.shape(LegendElement.propTypes))
    .isRequired,
}

Legend.defaultProps = {
  label: null,
}

export default Legend
