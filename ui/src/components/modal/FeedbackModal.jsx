import React from 'react'
import PropTypes from 'prop-types'
import { Text } from 'theme-ui'

import { formatPhone } from 'util/format'
import BoundModal from './BoundModal'

import { siteMetadata } from '../../../gatsby-config'

const { contactEmail, contactPhone, title } = siteMetadata

const FeedbackModal = ({ children }) => (
  <BoundModal
    title="Give your feedback to Blueprint Staff"
    anchorNode={children}
  >
    <Text as="p">
      The Blueprint and indicators are regularly revised based on input from
      people like you. Have a suggestion on how to improve the priorities? Let
      us know! We also welcome feedback on how to improve the Simple Viewer
      interface. South Atlantic staff will read and respond to your
      comments&mdash;we promise.
      <br />
      <br />
      <b>email</b>{' '}
      <a
        href={`mailto:${contactEmail}?subject=${title} Support (Simple Viewer) - report a problem`}
        target="_blank"
        rel="noopener noreferrer"
      >
        {contactEmail}
      </a>
      <br />
      <b>call</b>{' '}
      <a href={`tel:${contactPhone}`}>{formatPhone(contactPhone)}</a>
    </Text>
  </BoundModal>
)

FeedbackModal.propTypes = {
  children: PropTypes.node.isRequired,
}

export default FeedbackModal
