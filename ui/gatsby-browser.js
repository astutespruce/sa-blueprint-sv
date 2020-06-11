import * as Sentry from "@sentry/browser"
import GoogleAnalytics from "react-ga"

import { siteMetadata } from "./gatsby-config"

const { googleAnalyticsId, sentryDSN } = siteMetadata
export const onClientEntry = () => {
  if (googleAnalyticsId) {
    GoogleAnalytics.initialize(googleAnalyticsId)
  }

  if (sentryDSN) {
    Sentry.init({
      dsn: sentryDSN,
    })
    window.Sentry = Sentry
  }
}
