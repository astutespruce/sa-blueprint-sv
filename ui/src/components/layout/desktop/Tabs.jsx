import React from 'react'
import PropTypes from 'prop-types'
import { Box } from 'theme-ui'

import { Tabs as BaseTabs } from 'components/tabs'

const defaultTabs = [
  { id: 'info', label: 'Info' },
  { id: 'find', label: 'Find Location' },
  { id: 'contact', label: 'Contact' },
]

const unitTabs = [
  { id: 'selected-priorities', label: 'Priorities' },
  { id: 'selected-indicators', label: 'Indicators' },
  { id: 'selected-threats', label: 'Threats' },
  { id: 'selected-partners', label: 'Partners' },
]

const Tabs = ({ tab, mode, hasMapData, onChange }) => {
  let tabs = defaultTabs
  if (hasMapData) {
    if (mode === 'pixel') {
      tabs = unitTabs.slice(0, 2).concat([unitTabs[3]])
    } else {
      tabs = unitTabs
    }
  }

  return (
    <Box>
      <BaseTabs
        tabs={tabs}
        activeTab={tab}
        activeVariant="tabs.active"
        variant="tabs.default"
        onChange={onChange}
      />
    </Box>
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
