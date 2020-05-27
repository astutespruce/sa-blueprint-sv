/**
 * Flatten an array of arrays (2D) to an array (1D)
 * @param {Array} records
 */
export const flatten = records =>
  records.reduce((prev, record) => {
    prev.push(...record)
    return prev
  }, [])

/**
 * Convert an array to an object, indexing on values of field
 * @param {Array} records
 * @param {String} field
 */
export const indexBy = (records, field) =>
  records.reduce(
    (prev, record) => Object.assign(prev, { [record[field]]: record }),
    {}
  )

/**
 * Calculate the sum of an array of numbers
 * @param {Array} values - array of numbers
 */
export const sum = values => values.reduce((prev, value) => prev + value, 0)

export const sortByFunc = (field, ascending = true) => (a, b) => {
  if (a[field] < b[field]) {
    return ascending ? -1 : 1
  }
  if (a[field] > b[field]) {
    return ascending ? 1 : -1
  }
  return 0
}
