import { graphql, useStaticQuery } from "gatsby"

import { extractNodes } from "util/graphql"

/**
 * Provides corridors data in ascending order
 */
export const useCorridors = () => {
  const { corridors } = useStaticQuery(graphql`
    query {
      corridors: allCorridorsJson(sort: { fields: value, order: ASC }) {
        edges {
          node {
            label
            color
          }
        }
      }
    }
  `)

  return extractNodes(corridors)
}
