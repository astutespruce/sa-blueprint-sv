import { useStaticQuery, graphql } from 'gatsby'

import { indexBy, arrayToObject } from 'util/data'
import { extractNodes } from 'util/graphql'

/**
 * Provides Blueprint priority categories in decreasing priority order
 */
export const useBlueprintPriorities = () => {
  const query = useStaticQuery(graphql`
    query {
      allBlueprintJson(sort: { fields: value, order: DESC }) {
        edges {
          node {
            value
            color
            label
            labelColor
            percent
            description
          }
        }
      }
    }
  `).allBlueprintJson

  const all = extractNodes(query)
  const priorities = all.slice(0, all.length - 1)

  // create a lookup from uint32 color code to blueprint value
  const colors = priorities.map(({ value, color }) => {
    return {
      value,
      color: parseInt(color.slice(1, color.length), 16), // hex => uint32
    }
  })

  return {
    all,
    priorities,
    colorIndex: arrayToObject(
      colors,
      ({ color }) => color,
      ({ value }) => value
    ),
  }
}
