require('dotenv').config({
  path: `.env.${process.env.NODE_ENV}`,
})

module.exports = {
  siteMetadata: {
    siteUrl: process.env.SITE_URL || `https://localhost`,
    title: `South Atlantic Conservation Blueprint`,
    description: `Provides user interface to explore the South Atlantic Conservation Blueprint and custom reports for user-defined areas of interest`,
    author: `South Atlantic Conservation Blueprint`,
    contactEmail: `hilary_morris@fws.gov`,
    contactPhone: `9197070252`,
    blueprintVersion: '2021',
    apiToken: process.env.GATSBY_API_TOKEN,
    apiHost: process.env.GATSBY_API_HOST,
    tileHost: process.env.GATSBY_TILE_HOST,
    sentryDSN: process.env.GATSBY_SENTRY_DSN,
    sentryENV: process.env.GATSBY_SENTRY_ENV || 'development',
    googleAnalyticsId: process.env.GATSBY_GOOGLE_ANALYTICS_ID,
    mapboxToken: process.env.GATSBY_MAPBOX_API_TOKEN,
  },
  flags: {
    // FAST_DEV: true,
    DEV_SSR: true,
    FAST_REFRESH: true,
  },
  pathPrefix: process.env.SITE_ROOT_PATH || `/`,
  plugins: [
    {
      resolve: `gatsby-plugin-google-gtag`,
      options: {
        trackingIds: [process.env.GATSBY_GOOGLE_ANALYTICS_ID],
        gtagConfig: {
          anonymize_ip: true,
        },
        pluginConfig: {
          head: true,
          respectDNT: true,
        },
      },
    },
    `gatsby-plugin-react-helmet`,
    {
      resolve: `gatsby-source-filesystem`,
      options: {
        name: `images`,
        path: `${__dirname}/src/images`,
      },
    },
    {
      resolve: `gatsby-source-filesystem`,
      options: {
        name: `constants`,
        path: `${__dirname}/../constants`,
      },
    },
    {
      resolve: `gatsby-transformer-json`,
      options: {
        // name the top-level type after the filename
        typeName: ({ node }) => `${node.name}Json`,
      },
    },
    `gatsby-plugin-theme-ui`,
    `gatsby-transformer-sharp`,
    `gatsby-plugin-sharp`,
    {
      resolve: `gatsby-plugin-manifest`,
      options: {
        name: `South Atlantic Conservation Blueprint`,
        short_name: `SA Conservation Blueprint`,
        icon: 'src/images/logo.svg',
        start_url: `/`,
        background_color: `#0892d0`,
        theme_color: `#0892d0`,
        display: `minimal-ui`,
      },
    },
    {
      resolve: 'gatsby-plugin-robots-txt',
      options: {
        policy: [{ userAgent: '*', disallow: ['/services', '/api'] }],
      },
    },
  ],
}
