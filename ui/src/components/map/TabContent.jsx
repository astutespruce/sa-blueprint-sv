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

  const { type } = mapData

  if (type === 'pixel') {
    switch (tab) {
      case 'selected-priorities': {
        return (
          <PrioritiesTab
            blueprint={blueprint}
            corridors={corridors}
            blueprintAcres={blueprintAcres}
          />
        )
      }
      // TODO: implement indicators tab
      default: {
        return null
      }
    }
  }

  const {
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
          blueprint={blueprint}
          corridors={corridors}
          blueprintAcres={blueprintAcres}
        />
      )
    }
    case 'selected-indicators': {
      return (
        <IndicatorsTab
          unitType={type}
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
