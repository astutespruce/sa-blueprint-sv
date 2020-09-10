import React, { useState, useCallback } from 'react'
import { Box, Button, Flex } from 'theme-ui'
import { CommentDots, Envelope, FileAlt } from '@emotion-icons/fa-regular'

import { Link } from 'components/link'
import { Modal } from 'components/modal'
import { Feedback, Contact } from 'content/ContactTab'

const labelCSS = { marginLeft: '0.5rem', display: ['none', 'none', 'block'] }

const buttonProps = {
  variant: 'header',
  sx: {
    display: 'flex',
    alignItems: 'center',
  },
}

const HeaderButtons = () => {
  const [activeModal, setActiveModal] = useState(null)

  const handleClose = useCallback(() => {
    setActiveModal(() => null)
  }, [])

  const openFeedback = () => {
    setActiveModal(() => 'feedback')
  }

  const openContact = () => {
    setActiveModal(() => 'contact')
  }

  let modal = null
  if (activeModal === 'feedback') {
    modal = (
      <Modal
        title="Give your feedback to Blueprint staff"
        onClose={handleClose}
      >
        <Feedback />
      </Modal>
    )
  } else if (activeModal === 'contact') {
    modal = (
      <Modal
        title="Contact Blueprint staff for help using the Blueprint"
        onClose={handleClose}
      >
        <Contact />
      </Modal>
    )
  }

  return (
    <Flex sx={{ alignItems: 'center', flex: '0 0 auto' }}>
      <Button {...buttonProps} onClick={openFeedback}>
        <CommentDots size="1em" />
        <Box sx={{ ...labelCSS }}>Feedback</Box>
      </Button>

      <Button {...buttonProps} onClick={openContact}>
        <Envelope size="1em" />
        <Box sx={{ ...labelCSS }}>Contact Staff</Box>
      </Button>

      <Link to="/custom_report">
        <Button {...buttonProps}>
          <FileAlt size="1em" />
          <Box sx={{ ...labelCSS }}>Custom Report</Box>
        </Button>
      </Link>

      {modal}
    </Flex>
  )
}

export default HeaderButtons
