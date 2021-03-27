import React from 'react'
import PropTypes from 'prop-types'
import { Text } from 'theme-ui'

import { formatPhone } from 'util/format'
import BoundModal from './BoundModal'

import { siteMetadata } from '../../../gatsby-config'

const { contactEmail, contactPhone, title } = siteMetadata

const ContactModal = ({ children }) => (
  <BoundModal title="Contact Us" anchorNode={children}>
    <Text as="p">
      Do you have a question about the Blueprint? Would you like help using the
      Blueprint to support a proposal or inform a decision? South Atlantic staff
      are here to support you! We really mean it. It is what we do!
      <br />
      <br />
      <b>email</b>{' '}
      <a
        href={`mailto:${contactEmail}?subject=${title} Support (Simple Viewer)`}
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

ContactModal.propTypes = {
  children: PropTypes.node.isRequired,
}

export default ContactModal
