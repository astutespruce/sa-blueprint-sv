/** @jsx jsx */
import React from 'react'
import PropTypes from 'prop-types'
import { jsx } from 'theme-ui'

import {
  InfoCircle,
  Map,
  SearchLocation,
  QuestionCircle,
  Envelope,
  SkullCrossbones,
  ChartPie,
  SlidersH,
  UserFriends,
} from 'emotion-icons/fa-solid'

const Icon = ({ name, ...props }) => {
  switch (name) {
    case 'info': {
      return <InfoCircle {...props} />
    }
    case 'map':
    case 'unit-map': {
      return <Map {...props} />
    }
    case 'find': {
      return <SearchLocation {...props} />
    }
    case 'contact': {
      return <Envelope {...props} />
    }
    case 'unit-priorities': {
      return <ChartPie {...props} />
    }
    case 'unit-indicators': {
      return <SlidersH {...props} />
    }
    case 'unit-threats': {
      return <SkullCrossbones {...props} />
    }
    case 'unit-partners': {
      return <UserFriends {...props} />
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
