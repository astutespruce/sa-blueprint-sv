import React, { useState, useCallback } from "react"
import { Button, Flex } from "theme-ui"
import { CommentDots, Envelope, FileAlt } from "emotion-icons/fa-regular"

import { Link } from "components/Link"
import { Modal } from "components/Modal"
import { Feedback, Contact } from "content/ContactTab"

const iconCSS = { width: "1em", height: "1em", marginRight: "0.5em" }

const buttonProps = {
  variant: "header",
  sx: {
    display: "flex",
    alignItems: "center",
  },
}

const HeaderButtons = () => {
  const [activeModal, setActiveModal] = useState(null)

  const handleClose = useCallback(() => {
    setActiveModal(() => null)
  }, [])

  const openFeedback = () => {
    setActiveModal(() => "feedback")
  }

  const openContact = () => {
    setActiveModal(() => "contact")
  }

  let modal = null
  if (activeModal === "feedback") {
    modal = (
      <Modal
        title="Give your feedback to Blueprint staff"
        onClose={handleClose}
      >
        <Feedback />
      </Modal>
    )
  } else if (activeModal === "contact") {
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
    <Flex sx={{ alignItems: "center", flex: "0 0 auto" }}>
      <Button {...buttonProps} onClick={openFeedback}>
        <CommentDots css={iconCSS} />
        <div>Feedback</div>
      </Button>

      <Button {...buttonProps} onClick={openContact}>
        <Envelope css={iconCSS} />
        <div>Contact Staff</div>
      </Button>

      <Link to="/custom_report">
        <Button {...buttonProps}>
          <FileAlt css={iconCSS} />
          <div>Custom Report</div>
        </Button>
      </Link>

      {modal}
    </Flex>
  )
}

export default HeaderButtons
