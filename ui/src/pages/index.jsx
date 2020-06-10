import React from "react"

import { Layout, SelectedUnitProvider } from "components/layout"
import { MapContainer } from "components/map"

const IndexPage = () => (
  <SelectedUnitProvider>
    <Layout overflowY="hidden">
      <MapContainer />
    </Layout>
  </SelectedUnitProvider>
)

export default IndexPage
