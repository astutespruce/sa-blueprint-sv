import React, { memo, useState, useCallback } from 'react'
import { Box, Text } from 'theme-ui'

import { useBlueprintPriorities } from 'components/data'
import LegendElement from './LegendElement'

const Legend = () => {
  const [isOpen, setIsOpen] = useState(true)

  const handleClick = useCallback(() => {
    setIsOpen((prevIsOpen) => !prevIsOpen)
  }, [])

  const { priorities } = useBlueprintPriorities()

  return (
    <Box
      sx={{
        position: 'absolute',
        color: 'grey.9',
        bg: '#FFF',
        pointerEvents: 'auto',
        cursor: 'pointer',
        bottom: ['40px', '40px', '24px'],
        right: '10px',
        borderRadius: '0.25rem',
        boxShadow: '2px 2px 6px #333',
        maxWidth: '200px',
      }}
      onClick={handleClick}
    >
      {isOpen ? (
        <Box
          sx={{
            p: '1rem',
          }}
          title="Click to hide legend"
        >
          <Text sx={{ fontWeight: 'bold' }}>Blueprint Priority</Text>
          <Box sx={{ fontSize: 1 }}>
            {priorities.map((element) => (
              <Box
                key={element.label}
                sx={{
                  mt: '0.5rem',
                }}
              >
                <LegendElement {...element} />
              </Box>
            ))}
          </Box>
        </Box>
      ) : (
        <Text sx={{ py: '0.25rem', px: '0.5rem' }}>Show Legend</Text>
      )}
    </Box>
  )
}

Legend.propTypes = {}

export default memo(Legend)