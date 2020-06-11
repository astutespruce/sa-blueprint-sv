/** @jsx jsx */
import React, { useRef, useLayoutEffect, useState } from "react"
import BaseLineChart from "react-svg-line-chart"
import { Box, jsx } from "theme-ui"

const LineChart = props => {
  const node = useRef(null)
  const [loaded, setLoaded] = useState(false)

  useLayoutEffect(() => {
    const { clientWidth, clientHeight } = node.current
    setLoaded(true)
  }, [])

  console.log("render", node.current && node.current.clientHeight)

  return (
    <Box ref={node} sx={{ height: "100%", width: "100%" }}>
      {loaded ? (
        <BaseLineChart
          {...props}
          sx={{
            width: node.current.clientWidth,
            height: Math.max(node.current.clientHeight, 200),
          }}
          viewBoxHeight={node.current.clientHeight}
          viewBoxWidth={node.current.clientWidth}
        />
      ) : null}
    </Box>
  )
}

export default LineChart
