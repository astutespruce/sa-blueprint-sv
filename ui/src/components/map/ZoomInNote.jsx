import React, { memo } from "react"
import PropTypes from "prop-types"
import { Box, Text } from "theme-ui"

const ZoomInNote = ({ isVisible, isMobile, isPixelMode }) => {
  if (!isVisible) return null

  return (
    <Box
      sx={{
        fontSize: 0,
        position: "absolute",
        top: 0,
        left: isMobile ? 0 : "54px",
        right: isMobile ? 0 : "54px",
        textAlign: "center",
        py: "0.25em",
        px: "1em",
        bg: "#FFF",
        color: "grey.7",
        borderRadius: isMobile ? null : "0 0 1em 1em",
        boxShadow: "0 2px 6px #666",
      }}
    >
      <Text sx={{ mx: "auto" }}>Zoom in to select an area</Text>
    </Box>
  )
}

ZoomInNote.propTypes = {
  isVisible: PropTypes.bool,
  isMobile: PropTypes.bool,
  isPixelMode: PropTypes.bool,
}

ZoomInNote.defaultProps = {
  isVisible: true,
  isMobile: false,
  isPixelMode: false,
}

export default memo(ZoomInNote)
