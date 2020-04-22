import config from "../../../gatsby-config"

const { apiHost, apiToken } = config.siteMetadata

const customReportURL = `//${apiHost}/api/reports/custom/?token=${apiToken}`

// TODO: response is not JSON but attachment
const uploadFile = file => {
  const formData = new FormData()

  formData.append("file", file)
  formData.append("name", "TODO: name")

  return fetch(customReportURL, {
    method: "POST",
    body: formData,
  })
}

export default uploadFile
