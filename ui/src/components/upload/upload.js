import { hasWindow } from "util/dom"
import config from "../../../gatsby-config"

const { apiToken } = config.siteMetadata
let { apiHost } = config.siteMetadata

const pollInterval = 500 // milliseconds; 1 second
const jobTimeout = 600000 // milliseconds; 10 minutes

if (hasWindow && !apiHost) {
  apiHost = window.location.host
}

const API = `//${apiHost}/api/reports`

const uploadFile = async (file, name, onProgress) => {
  // NOTE: both file and name are required by API
  const formData = new FormData()
  formData.append("file", file)
  formData.append("name", name)

  const response = await fetch(`${API}/custom?token=${apiToken}`, {
    method: "POST",
    body: formData,
  })

  const { job, detail } = await response.json()

  if (response.status == 400) {
    // indicates error with user request, show error to user
    return { error: detail }
  }

  if (response.status != 200) {
    console.error("Bad response", response)
    throw new Error(response.statusText)
  }

  const result = await pollJob(job, onProgress)
  return result
}

const pollJob = async (jobId, onProgress) => {
  let time = 0

  while (time < jobTimeout) {
    const response = await fetch(`${API}/status/${jobId}`, {
      cache: "no-cache",
    })

    const {
      status = null,
      progress = null,
      detail: error = null, // error message
      result = null,
    } = await response.json()

    if (response.status != 200 || status === "failed") {
      if (error) {
        return { error }
      }

      throw Error(response.statusText)
    }

    if (status === "success") {
      return { result: `//${apiHost}${result}` }
    }

    if (progress != null) {
      onProgress(progress)
    }

    // sleep
    await new Promise(r => setTimeout(r, pollInterval))
    time += pollInterval
  }

  // if we got here, it meant that we hit a timeout error
  return {
    error:
      "timeout while creating report.  Your area of interest may be too big.",
  }
}

export { uploadFile }
