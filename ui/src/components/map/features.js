import {
  applyFactor,
  parsePipeEncodedValues,
  parseDeltaEncodedValues,
  parseDictEncodedValues,
} from "util/data"

/**
 * Unpack encoded attributes in feature data.
 * NOTE: indicators are returned by their index, not id.
 * @param {Object} properties
 */
export const unpackFeatureData = properties => {
  const values = Object.entries(properties)
    .map(([key, value]) => {
      if (!value || typeof value !== "string") {
        return [key, value]
      }

      if (value.indexOf("^") !== -1) {
        return [key, parseDeltaEncodedValues(value)]
      }
      if (value.indexOf(":") !== -1) {
        return [key, parseDictEncodedValues(value)]
      }
      if (value.indexOf("|") !== -1) {
        return [key, parsePipeEncodedValues(value)]
      }
      return [key, value]
    })
    .reduce((prev, [key, value]) => {
      prev[key] = value
      return prev
    }, {})

  // rescale specific things from percent * 10 back to percent

  values.blueprint = applyFactor(values.blueprint, 0.1)
  values.corridors = applyFactor(values.corridors, 0.1)
  if (values.indicators) {
    Object.keys(values.indicators).forEach(k => {
      values.indicators[k] = applyFactor(values.indicators[k], 0.1)
    })
  }
  if (values.slr) {
    values.slr = applyFactor(values.slr, 0.1)
  }
  if (values.urban) {
    values.urban = applyFactor(values.urban, 0.1)
  }
  if (values.ownership) {
    Object.keys(values.ownership).forEach(k => {
      values.ownership[k] = values.ownership[k] * 0.1
    })
  }
  if (values.protection) {
    Object.keys(values.protection).forEach(k => {
      values.protection[k] = values.protection[k] * 0.1
    })
  }

  return values
}
