import React from "react"
import PropTypes from "prop-types"

const PrioritiesTab = ({ blueprint }) => {
  return <div>Blueprint: {blueprint}</div>
}

PrioritiesTab.propTypes = {
  blueprint: PropTypes.arrayOf(PropTypes.number).isRequired,
}

export default PrioritiesTab
