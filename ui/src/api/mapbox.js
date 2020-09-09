import { config } from "components/map/config"
import { siteMetadata } from "../../gatsby-config"

const { mapboxToken } = siteMetadata

const apiURL = "https://api.mapbox.com/geocoding/v5/mapbox.places"
const { bounds } = config
const types = ["region", "place", "poi"]

export const searchPlaces = query => {
  const controller = new AbortController()

  // TODO: limit bounds: https://docs.mapbox.com/api/search/
  const url = `${apiURL}/${encodeURI(
    query
  )}.json?language=en-US&fuzzyMatch=false&country=us&bbox=${bounds.toString()}&types=${types.toString()}&access_token=${mapboxToken}`

  const promise = fetch(url, {
    method: "GET",
    mode: "cors",
    signal: controller.signal,
  })
    .then(response => {
      if (!response.ok) {
        return Promise.reject(new Error(response.statusText))
      }

      return response.json().catch(error => {
        return Promise.reject(new Error("Invalid JSON: ", error.message))
      })
    })
    .then(({ features = [] }) => {
      console.log("got features")
      const results = features.map(
        ({
          id,
          center: [longitude, latitude],
          text: name,
          matching_text: altName,
          properties: { address },
          context = [],
        }) => {
          const [city] = context.filter(({ id }) => id.startsWith("place."))
          const [state] = context.filter(({ id }) => id.startsWith("region."))

          const parts = []
          if (address) {
            parts.push(address)
          }
          if (city) {
            parts.push(city.text)
          }
          if (state) {
            parts.push(state.text)
          }

          return {
            id,
            longitude,
            latitude,
            name: altName || name,
            address: parts.length ? parts.join(", ") : null,
          }
        }
      )

      console.log("results", results)
      return results
      // return Promise.resolve(results)
    })

    .catch(error => {
      return Promise.reject(new Error(error.message))
    })

  promise.cancel = () => {
    controller.abort()

    // make sure to resolve promise or it raises an error on cancel
    return Promise.resolve()
  }

  return promise
}
