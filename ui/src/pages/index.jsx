import React from "react"
import PropTypes from "prop-types"

import Layout from "components/layout"
import { MapContainer } from "components/map"

const IndexPage = () => (
  <Layout overflowY="hidden">
    <MapContainer />
  </Layout>
)

export default IndexPage
