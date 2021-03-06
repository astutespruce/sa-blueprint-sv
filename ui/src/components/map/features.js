import {
  applyFactor,
  parsePipeEncodedValues,
  parseDeltaEncodedValues,
  parseDictEncodedValues,
} from 'util/data'

const isEmpty = (text) => {
  if (!text) {
    return true
  }
  if (text === '"') {
    return true
  }

  return false
}

/**
 * Unpack encoded attributes in feature data.
 * NOTE: indicators are returned by their index, not id.
 * @param {Object} properties
 */
export const unpackFeatureData = (properties) => {
  const values = Object.entries(properties)
    .map(([key, value]) => {
      if (!value || typeof value !== 'string') {
        return [key, value]
      }

      if (isEmpty(value)) {
        return [key, null]
      }

      if (key === 'name') {
        return [key, value]
      }

      if (value.indexOf('^') !== -1) {
        return [key, parseDeltaEncodedValues(value)]
      }
      if (value.indexOf(':') !== -1) {
        return [key, parseDictEncodedValues(value)]
      }
      if (value.indexOf('|') !== -1) {
        return [key, parsePipeEncodedValues(value)]
      }
      return [key, value]
    })
    .reduce((prev, [key, value]) => {
      // eslint-disable-next-line no-param-reassign
      prev[key] = value
      return prev
    }, {})

  // rescale specific things from percent * 10 back to percent

  values.blueprint = values.blueprint ? applyFactor(values.blueprint, 0.1) : []
  values.corridors = values.corridors ? applyFactor(values.corridors, 0.1) : []

  // extract percents
  if (values.indicators) {
    Object.keys(values.indicators).forEach((k) => {
      const percent = applyFactor(values.indicators[k], 0.1)

      values.indicators[k] = {
        percent,
      }
    })
  } else {
    values.indicators = []
  }

  if (values.slr) {
    values.slr = applyFactor(values.slr, 0.1)
  }

  if (values.urban) {
    values.urban = applyFactor(values.urban, 0.1)
  }

  if (values.ownership) {
    Object.keys(values.ownership).forEach((k) => {
      values.ownership[k] *= 0.1
    })
  }

  if (values.protection) {
    Object.keys(values.protection).forEach((k) => {
      values.protection[k] *= 0.1
    })
  }

  console.log('transformed feature data', values)

  return values
}
