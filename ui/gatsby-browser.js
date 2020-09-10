import * as Sentry from "@sentry/browser"

import { siteMetadata } from "./gatsby-config"

const { sentryDSN } = siteMetadata
export const onClientEntry = () => {
  if (sentryDSN) {
    Sentry.init({
      dsn: sentryDSN,
    })
    window.Sentry = Sentry
  }
}
