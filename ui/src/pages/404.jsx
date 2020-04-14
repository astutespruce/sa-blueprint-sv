import React from "react"
import { Heading, Flex } from "theme-ui"
import Layout from "components/layout"

const NotFoundPage = () => (
  <Layout title="404: Not found">
    <Flex
      sx={{
        alignItems: "center",
        justifyContent: "center",
        flexDirection: "column",
        height: "100%",
      }}
    >
      <Heading as="h1">NOT FOUND</Heading>
    </Flex>
  </Layout>
)

export default NotFoundPage
