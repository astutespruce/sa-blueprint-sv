import React, { memo, useState, useCallback } from "react"
import PropTypes from "prop-types"
import { Box, Text } from "theme-ui"

import { useBlueprintPriorities } from "components/data"

import Legend from "./Legend"

const coreCSS = { position: "absolute", color: "grey.8", bg: "#FFF" }

const desktopCSS = {
  cursor: "pointer",
  bottom: ["40px", "40px", "24px"],
  right: "10px",
  borderRadius: "0.25rem",
  boxShadow: "2px 2px 6px #333",
  maxWidth: "200px",
}
const mobileCSS = {
  bottom: 0,
  left: 0,
  right: 0,
  borderTop: "1px solid",
  borderTopColor: "grey.7",
}

const LegendContainer = ({ isMobile }) => {
  const [isOpen, setIsOpen] = useState(true)

  const handleClick = useCallback(() => {
    if (isMobile) {
      return
    }
    setIsOpen(prevIsOpen => !prevIsOpen)
  }, [])

  const { priorities } = useBlueprintPriorities()
  const legend = [
    {
      id: "blueprint",
      label: "Blueprint Priority",
      elements: isMobile
        ? priorities.map(({ label, ...rest }) => ({
            ...rest,
            label: label.replace(" priority", ""),
          }))
        : priorities,
    },
  ]
  const legendCSS = isMobile ? mobileCSS : desktopCSS

  return (
    <Box
      sx={{
        ...coreCSS,
        ...legendCSS,
      }}
      onClick={handleClick}
    >
      {isOpen ? (
        <Box
          sx={{
            p: isMobile ? "0.5rem" : "1rem",
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
                <Legend {...group} isMobile={isMobile} />
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
  isMobile: PropTypes.bool,
}

LegendContainer.defaultProps = {
  isMobile: false,
}

// TODO: memoize
export default LegendContainer
