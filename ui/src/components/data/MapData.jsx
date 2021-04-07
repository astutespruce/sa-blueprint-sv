import React, { useState, useCallback, useContext, createContext } from 'react'
import PropTypes from 'prop-types'

const Context = createContext()

export const Provider = ({ children }) => {
  const [{ mapMode, data, selectedIndicator }, setState] = useState({
    mapMode: 'unit', // pixel or unit
    data: null,
    selectedIndicator: null,
  })

  const setData = useCallback((newData) => {
    setState((prevState) => ({
      ...prevState,
      data: newData,
      selectedIndicator: newData === null ? null : prevState.selectedIndicator,
    }))
  }, [])

  const unsetData = useCallback(() => {
    setData(null)
  }, [setData])

  const setMapMode = useCallback((mode) => {
    setState(() => ({
      mapMode: mode,
      data: null,
    }))
  }, [])

  const setSelectedIndicator = useCallback((newSelectedIndicator) => {
    setState((prevState) => ({
      ...prevState,
      selectedIndicator: newSelectedIndicator,
    }))
  }, [])

  return (
    <Context.Provider
      value={{
        data,
        setData,
        unsetData,
        mapMode,
        setMapMode,
        selectedIndicator,
        setSelectedIndicator,
      }}
    >
      {children}
    </Context.Provider>
  )
}

Provider.propTypes = {
  children: PropTypes.node.isRequired,
}

export const useMapData = () => useContext(Context)
