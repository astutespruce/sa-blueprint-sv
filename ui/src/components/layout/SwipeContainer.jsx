import React, { useState, useRef } from "react"
import PropTypes from "prop-types"

import { Box, Flex } from "theme-ui"

const SwipeContainer = ({ children, minDelta, onSwipeMove, onSwipeEnd }) => {
  const node = useRef(null)
  const [x, setX] = useState(null)

  // TODO: set number of viewports left or right instead
  const [swipe, setSwipe] = useState(null)
  const [transform, setTransform] = useState(0)

  const handleTouchStart = ({ touches: [{ clientX }] }) => {
    console.log("touch start")
    setX(clientX)
  }
  const handleTouchMove = ({ touches: [{ clientX }] }) => {
    const delta = x ? clientX - x : 0
    const width = node.current.clientWidth

    // TODO: min and max
    setTransform((100 * delta) / width)

    onSwipeMove(delta)
    console.log("touch move", delta)

    if (Math.abs(delta) < minDelta) {
      setSwipe(null)
      return
    }

    if (delta < 0) {
      setSwipe("left")
    } else {
      setSwipe("right")
    }
  }
  const handleTouchEnd = () => {
    onSwipeEnd(swipe)
    setX(null)
  }

  return (
    <Box sx={{ overflowX: "hidden" }}>
      <Flex
        ref={node}
        sx={{
          willChange: "transform",
          transform: `translate(${transform}%, 0)`,
        }}
        onTouchStart={handleTouchStart}
        onTouchMove={handleTouchMove}
        onTouchEnd={handleTouchEnd}
      >
        {children}
      </Flex>
    </Box>
  )
}

SwipeContainer.propTypes = {
  children: PropTypes.node.isRequired,
  onSwipeMove: PropTypes.func.isRequired,
  onSwipeEnd: PropTypes.func.isRequired,
  minDelta: PropTypes.number,
}

SwipeContainer.defaultProps = {
  minDelta: 30,
}

export default SwipeContainer
