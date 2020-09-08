import { graphql, useStaticQuery } from "gatsby"
import { extractNodes } from "util/graphql"

export const useIndicators = () => {
  const { ecosystems, indicators } = useStaticQuery(graphql`
    query {
      ecosystems: allEcosystemsJson {
        edges {
          node {
            id
            label
            color
            borderColor
            indicators
          }
        }
      }
      indicators: allIndicatorsJson {
        edges {
          node {
            id
            label
            datasetID
            description
            units
            domain
            continuous
            goodThreshold
            values {
              value
              label
            }
          }
        }
      }
    }
  `)

  return {
    ecosystems: extractNodes(ecosystems),
    indicators: extractNodes(indicators),
  }
}
