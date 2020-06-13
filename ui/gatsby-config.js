require("dotenv").config({
  path: `.env.${process.env.NODE_ENV}`,
})

module.exports = {
  siteMetadata: {
    title: `South Atlantic Conservation Blueprint 2.x`,
    description: `Provides custom reports for user-defined areas of interest`,
    author: `South Atlantic Conservation Blueprint`,
    contactEmail: `hilary_morris@fws.gov`,
    contactPhone: `19197070252`,
    apiToken: process.env.GATSBY_API_TOKEN,
    apiHost: process.env.GATSBY_API_HOST,
    tileHost: process.env.GATSBY_TILE_HOST,
    sentryDSN: process.env.GATSBY_SENTRY_DSN,
    googleAnalyticsId: process.env.GATSBY_GOOGLE_ANALYTICS_ID,
    mapboxToken: process.env.GATSBY_MAPBOX_API_TOKEN,
  },
  plugins: [
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
        name: `config`,
        path: `${__dirname}/config`,
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
      resolve: `gatsby-plugin-google-analytics`,
      options: {
        trackingId: process.env.GATSBY_GOOGLE_ANALYTICS_ID,
        anonymize: true,
      },
    },

    // TODO:
    // {
    //   resolve: `gatsby-plugin-manifest`,
    //   options: {
    //     name: `sa-reports`,
    //     short_name: `sa-reports`,
    //     start_url: `/`,
    //     background_color: `#663399`,
    //     theme_color: `#663399`,
    //     display: `minimal-ui`,
    //   },
    // },
  ],
}
