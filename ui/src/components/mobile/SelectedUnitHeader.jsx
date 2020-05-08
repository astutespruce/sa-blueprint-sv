import React from "react"
import PropTypes from "prop-types"
import { Button, Flex, Text } from "theme-ui"
import { TimesCircle } from "emotion-icons/fa-regular"

const SelectedUnitHeader = ({ name, onClose }) => {
  return (
    <Flex
      sx={{
        justifyContent: "space-between",
        alignItems: "flex-start",
        color: "#FFF",
        bg: "primary",
        boxShadow: "0 2px 6px #333",
        p: "0.5rem",
        position: "absolute",
        top: 0,
        left: 0,
        right: 0,
        zIndex: 20000,
      }}
    >
      <Text sx={{ px: "0.5rem", fontSize: 2 }}>{name}</Text>
      <Button
        variant="mobileHeaderClose"
        onClick={onClose}
        sx={{ flex: "0 0 auto", margin: 0, padding: 0 }}
      >
        <TimesCircle
          css={{
            width: "1.5em",
            height: "1.5em",
          }}
        />
      </Button>
    </Flex>
  )
}

SelectedUnitHeader.propTypes = {
  name: PropTypes.string.isRequired,
  onClose: PropTypes.func.isRequired,
}

export default SelectedUnitHeader
