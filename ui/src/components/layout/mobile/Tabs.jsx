import React from 'react'
import PropTypes from 'prop-types'

import { Tabs as BaseTabs } from 'components/tabs'

const defaultTabs = [
  { id: 'info', label: 'Info' },
  { id: 'map', label: 'Map' },
  { id: 'find', label: 'Find Location' },
  { id: 'contact', label: 'Contact' },
]

const unitTabs = [
  { id: 'mobile-selected-map', label: 'Map' },
  { id: 'selected-priorities', label: 'Priorities' },
  { id: 'selected-indicators', label: 'Indicators' },
  { id: 'selected-threats', label: 'Threats' },
  { id: 'selected-partners', label: 'Partners' },
]

const Tabs = ({ tab, mode, hasMapData, onChange }) => {
  let tabs = defaultTabs
  if (hasMapData) {
    if (mode === 'pixel') {
      tabs = unitTabs.slice(0, 2)
    } else {
      tabs = unitTabs
    }
  }

  return (
    <BaseTabs
      tabs={tabs}
      activeTab={tab}
      activeVariant="tabs.mobileActive"
      variant="tabs.mobile"
      onChange={onChange}
    />
  )
}

Tabs.propTypes = {
  tab: PropTypes.string.isRequired,
  onChange: PropTypes.func.isRequired,
  mode: PropTypes.string.isRequired,
  hasMapData: PropTypes.bool,
}

Tabs.defaultProps = {
  hasMapData: false,
}

export default Tabs
