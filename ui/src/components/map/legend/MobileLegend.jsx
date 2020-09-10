import React, { memo, useState, useCallback } from 'react'
import PropTypes from 'prop-types'
import { Box, Flex, Text } from 'theme-ui'

import { useBlueprintPriorities } from 'components/data'

import LegendElement from './LegendElement'

const MobileLegend = () => {
  const [isOpen, setIsOpen] = useState(true)

  const handleClick = useCallback(() => {
    setIsOpen((prevIsOpen) => !prevIsOpen)
  }, [])

  const { priorities } = useBlueprintPriorities()
  const elements = priorities.map(({ label, ...rest }) => ({
    ...rest,
    label: label.replace(' priority', ''),
  }))

  return (
    <Box
      sx={{
        //   position: "absolute",
        color: 'grey.8',
        bg: '#FFF',
        pointerEvents: 'auto',
        bottom: 0,
        left: 0,
        right: 0,
        borderTop: '1px solid',
        borderTopColor: 'grey.7',
      }}
      onClick={handleClick}
    >
      {isOpen ? (
        <Box
          sx={{
            p: '0.5rem',
          }}
          title="Click to hide legend"
        >
          <Box sx={{ fontSize: 0 }}>
            <Text sx={{ lineHeight: 1, fontWeight: 'bold' }}>
              Blueprint Priority
            </Text>
            <Flex
              sx={{
                alignItems: 'flex-end',
                justifyContent: 'space-between',
              }}
            >
              {elements.map((element) => (
                <Box
                  key={element.label}
                  sx={{
                    mt: '0.5rem',
                  }}
                >
                  <LegendElement {...element} />
                </Box>
              ))}
            </Flex>
          </Box>
        </Box>
      ) : (
        <Text sx={{ fontSize: 0, py: '0.25rem', px: '0.5rem' }}>Legend</Text>
      )}
    </Box>
  )
}

export default memo(MobileLegend)
