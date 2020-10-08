import { hasWindow, saveToStorage, encodeParams } from 'util/dom'
import { captureException } from 'util/log'
import config from '../../../gatsby-config'

const { apiToken } = config.siteMetadata
let { apiHost } = config.siteMetadata

const pollInterval = 1000 // milliseconds; 1 second
const jobTimeout = 600000 // milliseconds; 10 minutes

if (hasWindow && !apiHost) {
  apiHost = `//${window.location.host}`
}

const API = `${apiHost}/api/reports`

export const uploadFile = async (file, name, onProgress) => {
  // NOTE: both file and name are required by API
  const formData = new FormData()
  formData.append('file', file)
  formData.append('name', name)

  const response = await fetch(`${API}/custom?token=${apiToken}`, {
    method: 'POST',
    body: formData,
  })

  const json = await response.json()
  const { job, detail } = json

  if (response.status === 400) {
    // indicates error with user request, show error to user

    // just for logging
    console.error('Bad upload request', json)
    captureException('Bad upload request', json)

    return { error: detail }
  }

  if (response.status !== 200) {
    console.error('Bad response', json)

    captureException('Bad upload response', json)

    throw new Error(response.statusText)
  }

  const result = await pollJob(job, onProgress)
  return result
}

export const createSummaryUnitReport = async (id, type, onProgress) => {
  let unitType = null

  if (type === 'subwatershed') {
    unitType = 'huc12'
  } else if (type === 'marine lease block') {
    unitType = 'marine_blocks'
  }

  const response = await fetch(`${API}/${unitType}/${id}?token=${apiToken}`, {
    method: 'POST',
  })

  const json = await response.json()
  const { job, detail } = json

  if (response.status === 400) {
    // indicates error with user request, show error to user

    // just for logging
    console.error('Bad create summary report request', json)
    captureException('Bad create summary report request', json)

    return { error: detail }
  }

  if (response.status !== 200) {
    console.error('Bad response', json)
    captureException('Bad upload response', json)

    throw new Error(response.statusText)
  }

  const result = await pollJob(job, onProgress)
  return result
}

const pollJob = async (jobId, onProgress) => {
  let time = 0

  while (time < jobTimeout) {
    const response = await fetch(`${API}/status/${jobId}`, {
      cache: 'no-cache',
    })

    const json = await response.json()
    const {
      status = null,
      progress = null,
      detail: error = null, // error message
      result = null,
    } = json

    if (response.status != 200 || status === 'failed') {
      captureException('Report job failed', json)
      if (error) {
        return { error }
      }

      throw Error(response.statusText)
    }

    if (status === 'success') {
      return { result: `${apiHost}${result}` }
    }

    if (progress != null) {
      onProgress(progress)
    }

    // sleep
    await new Promise((r) => setTimeout(r, pollInterval))
    time += pollInterval
  }

  // if we got here, it meant that we hit a timeout error
  captureException('Report job timed out')

  return {
    error:
      'timeout while creating report.  Your area of interest may be too big.',
  }
}

export const submitUserInfo = async (userInfo) => {
  const { userEmail, userName, userOrg, userUse } = userInfo
  console.log('submit user info', userEmail, userName, userOrg, userUse)

  const formURL = `https://forms.office.com/formapi/api/0693b5ba-4b18-4d7b-9341-f32f400a5494/users/765228b1-d0d0-4438-812e-51cbb57819f1/forms('urWTBhhLe02TQfMvQApUlLEoUnbQ0DhEgS5Ry7V4GfFURFMxWkczNDM4NkFPNloySTBHMjhXVVZIWC4u')/responses`
  const questionIds = {
    userEmail: 'r792746f558e844148724fa5fcfec95fc',
  }

  const answers = Object.entries(questionIds).map(([field, questionId]) => ({
    questionId,
    answer1: userInfo[field],
  }))

  try {
    // in no-cors mode, we can submit but not receive content
    await fetch(formURL, {
      method: 'POST',
      mode: 'no-cors',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: encodeParams({ answers: JSON.stringify(answers) }),
    })

    saveToStorage('reportForm', userInfo)
  } catch (ex) {
    console.error('Could not submit user info to MS Form', userInfo)
  }
}

//

// import { siteMetadata } from '../../../gatsby-config'

// const {
//   mailchimpConfig: { userID, formID, formURL },
// } = siteMetadata

// if (!(formURL && userID && formID)) {
//   console.error('Mail chimp form env vars need to be provided in .env file')
// }

// Note: we have to add -json to the end of the regular form URL, make sure it is formatted correctly in .env.*
// fetchJSONP(
//   `${formURL}-json?${encodeParams({
//     u: userID,
//     id: formID,
//     ...data,
//   })}`,
//   {
//     jsonpCallback: 'c',
//   }
// )
//   .then(response => {
//     return response.json()
//   })
//   .then(({ result, msg }) => {
//     console.log('json', result, msg)
//     if (result === 'error') {
//       if (msg.search('already subscribed') !== -1) {
//         // this is an error ot Mailchimp, but not a problem for us
//         saveToStorage('downloadForm', data)
//         setState({ isPending: false, isError: false, isSuccess: true })

//         onContinue()
//       } else {
//         setState({ isPending: false, isError: true })
//         // TODO: report error to sentry
//       }
//     } else {
//       // assume it was successful
//       saveToStorage('downloadForm', data)
//       setState({ isPending: false, isError: false, isSuccess: true })
//       // TODO:

//       onContinue()
//     }
//   })
//   .catch(error => {
//     console.error(error)
//     setState({ isPending: false, isError: true })

//     // TODO: report error to sentry
//   })
// }
