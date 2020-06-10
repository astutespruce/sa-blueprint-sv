import React, { useState } from "react"
import { Box, Button, Flex, Heading, Text } from "theme-ui"
import { Play } from "emotion-icons/fa-solid"
import YouTube from "react-youtube"

import { OutboundLink } from "components/link"
import { Modal } from "components/Modal"

const Intro = () => {
  const [videoOpen, setVideoOpen] = useState(false)

  const openVideo = () => {
    setVideoOpen(() => true)
  }

  const closeVideo = () => {
    setVideoOpen(() => false)
  }

  return (
    <>
      <Box as="section">
        {/* <Heading as="h3" sx={{ mb: "0.5rem" }}>
          South Atlantic Conservation Blueprint Simple Viewer
        </Heading> */}

        <p>
          The{" "}
          <OutboundLink to="http://www.southatlanticlcc.org/blueprint/">
            Conservation Blueprint
          </OutboundLink>{" "}
          is a living spatial plan to conserve natural and cultural resources
          for future generations. It identifies priority areas for shared
          conservation action. Blueprint 2.x is completely data-driven,
          prioritizing the lands and waters of the South Atlantic region based
          on ecosystem indicator models and a connectivity analysis. Better
          indicator condition suggests higher ecosystem integrity and higher
          importance for natural and cultural resources across all ecosystems
          collectively. So far, more than 500 people from 150 organizations
          actively participated in the collaborative development of the
          Blueprint.
        </p>

        <Flex sx={{ justifyContent: "center" }}>
          <Button
            onClick={openVideo}
            sx={{ display: "flex", alignItems: "center" }}
          >
            <Play css={{ height: "1em", width: "1em", marginRight: "0.5em" }} />
            <Text>Overview Video</Text>
          </Button>
        </Flex>

        <p>
          This <b>Simple Viewer</b> summarizes the Blueprint priorities and
          supporting information within subwatersheds and marine lease blocks.
          In a new pixel mode, you can also explore pixel-level details of what
          indicators are driving the Blueprint priorities.
        </p>
      </Box>

      {videoOpen && (
        <Modal
          title="Blueprint Simple Viewer - Overview Video"
          width="840px"
          onClose={closeVideo}
        >
          <YouTube
            videoId="wSPbCiCTQOM"
            opts={{ height: "464", width: "100%" }}
          />
        </Modal>
      )}
    </>
  )
}

export default Intro
