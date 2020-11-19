import React from 'react'
import PropTypes from 'prop-types'
import {
  InfoTab,
  ContactTab,
  FindLocationTab,
  PrioritiesTab,
  IndicatorsTab,
  ThreatsTab,
  PartnersTab,
} from 'content'

const TabContent = ({ tab, mapData }) => {
  if (mapData === null) {
    switch (tab) {
      case 'info': {
        return <InfoTab />
      }
      case 'find': {
        return <FindLocationTab />
      }
      case 'contact': {
        return <ContactTab />
      }
      default: {
        // includes 'map
        return null
      }
    }
  }

  const {
    type,
    acres: unitAcres,
    blueprint,
    blueprint_total: blueprintAcres,
    shape_mask: analysisAcres,
    corridors,
    indicators,
    slr,
    urban,
    ownership,
    protection,
    counties,
  } = mapData

  switch (tab) {
    case 'selected-priorities': {
      return (
        <PrioritiesTab
          type={type}
          blueprint={blueprint}
          corridors={corridors}
          blueprintAcres={blueprintAcres}
        />
      )
    }
    case 'selected-indicators': {
      return (
        <IndicatorsTab
          type={type}
          blueprintAcres={blueprintAcres}
          analysisAcres={analysisAcres}
          indicators={indicators}
        />
      )
    }
    case 'selected-threats': {
      return <ThreatsTab unitType={type} slr={slr} urban={urban} />
    }
    case 'selected-partners': {
      return (
        <PartnersTab
          unitType={type}
          analysisAcres={unitAcres}
          ownership={ownership}
          protection={protection}
          counties={counties}
        />
      )
    }
    default: {
      // includes 'mobile-selected-map'
      return null
    }
  }
}

TabContent.propTypes = {
  tab: PropTypes.string.isRequired,
  mapData: PropTypes.object,
}

TabContent.defaultProps = {
  mapData: null,
}

export default TabContent
