import React, { useRef, useLayoutEffect, useState } from "react"
import { Box } from "theme-ui"

import InnerChart from "./Chart"

const Chart = props => {
  const node = useRef(null)
  const [loaded, setLoaded] = useState(false)

  // layout effect is used to know when we have loaded, so we
  // can set the SVG based on the container height
  useLayoutEffect(() => {
    const { clientWidth, clientHeight } = node.current
    setLoaded(true)
  }, [])

  return (
    <Box
      ref={node}
      sx={{ height: "100%", width: "100%", border: "1px solid red" }}
    >
      {loaded ? (
        <InnerChart
          {...props}
          width={node.current.clientWidth}
          height={node.current.clientHeight}
        />
      ) : null}
    </Box>
  )
}

export default Chart
