import React from "react"
import { Divider } from "theme-ui"

import Intro from "./Intro"
import Blueprint from "./Blueprint"
import Instructions from "./Instructions"
import Credits from "./Credits"

const InfoTab = () => {
  return (
    <>
      <Intro />
      <Blueprint />
      <Divider />
      <Instructions />
      <Divider />
      <Credits />
    </>
  )
}

export default InfoTab
