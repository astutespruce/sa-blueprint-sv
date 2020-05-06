/** @jsx jsx */
import React from "react"
import PropTypes from "prop-types"
import { jsx } from "theme-ui"

import {
  InfoCircle,
  Map,
  SearchLocation,
  QuestionCircle,
  Envelope,
} from "emotion-icons/fa-solid"

const Icon = ({ name, ...props }) => {
  switch (name) {
    case "info": {
      return <InfoCircle {...props} />
    }
    case "map": {
      return <Map {...props} />
    }
    case "find": {
      return <SearchLocation {...props} />
    }
    case "contact": {
      return <Envelope {...props} />
    }
    default: {
      // fallthrough to make sure we always get an icon
      return <QuestionCircle {...props} />
    }
  }
}

Icon.propTypes = {
  name: PropTypes.string.isRequired,
}

export default Icon
