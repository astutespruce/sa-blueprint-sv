const path = require("path")
/**
 * Enable absolute imports with `/src` as root.
 * See: https://github.com/alampros/gatsby-plugin-resolve-src/issues/4
 */
exports.onCreateWebpackConfig = ({ actions, stage, loaders }) => {
  const config = {
    resolve: {
      modules: [path.resolve(__dirname, "src"), "node_modules"],
    },
    // per https://github.com/gatsbyjs/gatsby/issues/564
    node: {
      fs: "empty",
    },
  }

  actions.setWebpackConfig(config)
}
