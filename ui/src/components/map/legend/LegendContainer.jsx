import React, { memo, useState, useCallback } from "react"
import PropTypes from "prop-types"
import { dequal as deepEqual } from "dequal"
import { Box, Text } from "theme-ui"

import Legend from "./Legend"

const LegendContainer = ({ legend }) => {
  const [isOpen, setIsOpen] = useState(true)

  const handleClick = useCallback(() => {
    setIsOpen(prevIsOpen => !prevIsOpen)
  }, [])

  return (
    <Box
      sx={{
        position: "absolute",
        bottom: "24px",
        right: "10px",
        bg: "#FFF",
        borderRadius: "0.25rem",
        boxShadow: "2px 2px 6px #333",
        maxWidth: "200px",
        color: "grey.8",
        cursor: "pointer",
      }}
      onClick={handleClick}
    >
      {isOpen ? (
        <Box
          sx={{
            p: "1rem",
          }}
          title="Click to hide legend"
        >
          {legend.map((group, i) => (
            <React.Fragment key={group.id}>
              {i > 0 ? (
                <Box
                  sx={{
                    mt: "0.5rem",
                    pt: "0.5rem",
                    borderTop: "1px solid",
                    borderTopColor: "grey.2",
                  }}
                />
              ) : null}
              <Box key={legend.id}>
                <Legend {...group} />
              </Box>
            </React.Fragment>
          ))}
        </Box>
      ) : (
        <Text sx={{ py: "0.25rem", px: "0.5rem" }}>Show Legend</Text>
      )}
    </Box>
  )
}

LegendContainer.propTypes = {
  legend: PropTypes.arrayOf(PropTypes.shape(Legend.propTypes)).isRequired,
}

// Only render legend container if underlying values actually changed
export default memo(LegendContainer, (prev, next) => {
  return deepEqual(prev, next)
})
