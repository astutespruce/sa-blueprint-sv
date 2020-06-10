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
        flex: "1 1 auto",
        alignItems: "center",
        p: "0.25rem",
        lineHeight: 1.2,
      }}
    >
      <Text sx={{ pr: "0.5rem", fontSize: 2 }}>{name}</Text>
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
