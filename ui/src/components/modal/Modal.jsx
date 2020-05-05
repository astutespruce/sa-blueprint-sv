import React from "react"
import { createPortal } from "react-dom"
import PropTypes from "prop-types"
import { Box, Button, Flex, Heading } from "theme-ui"
import { TimesCircle } from "emotion-icons/fa-regular"

const absPostionCSS = {
  position: "absolute",
  top: 0,
  bottom: 0,
  left: 0,
  right: 0,
}

const index = ({ children, title, onClose }) => {
  const handleClose = () => {
    onClose()
  }

  return createPortal(
    <Flex
      sx={{
        ...absPostionCSS,
        zIndex: 10000,
        alignItems: "center",
        justifyContent: "center",

        overflow: "auto",
      }}
    >
      <Box
        onClick={handleClose}
        sx={{
          ...absPostionCSS,
          zIndex: 1,
          bg: "rgba(0,0,0,0.5)",
        }}
      />

      <Box
        sx={{
          maxWidth: ["100%", "500px"],
          p: "0.5rem",
          background: "#fff",
          zIndex: 2,
          borderRadius: "1rem",
          boxShadow: "1px 1px 6px #000",
        }}
      >
        <Heading
          as="h3"
          sx={{
            pb: "0.5rem",
            borderBottom: "1px solid",
            borderBottomColor: "grey.3",
          }}
        >
          <Flex
            sx={{
              justifyContent: "space-between",
              alignItems: "flex-start",
            }}
          >
            <Box sx={{ p: "0.5rem" }}>{title}</Box>
            <Button
              variant="close"
              onClick={handleClose}
              sx={{ flex: "0 0 auto", margin: "0" }}
            >
              <TimesCircle
                css={{
                  width: "1.5em",
                  height: "1.5em",
                }}
              />
            </Button>
          </Flex>
        </Heading>

        <Box sx={{ px: "0.5rem" }}>{children}</Box>
      </Box>
    </Flex>,
    document.body
  )
}

index.propTypes = {
  title: PropTypes.string.isRequired,
  children: PropTypes.node.isRequired,
  onClose: PropTypes.func.isRequired,
}

export default index
