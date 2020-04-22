import React from "react"
import PropTypes from "prop-types"
import { graphql } from "gatsby"

import Layout from "components/layout"
import { BannerImage } from "components/image"
import { UploadContainer } from "components/upload"

const IndexPage = ({ data: { headerImage } }) => (
  <Layout title="Home">
    <BannerImage
      title="Create a Custom Report"
      src={headerImage}
      url="https://www.flickr.com/photos/usfwssoutheast/26871026541/"
      credit="U.S. Fish and Wildlife Service Southeast Region"
      caption="Black Skimmers"
      height="10rem"
      maxHeight="10rem"
    />

    <UploadContainer />
  </Layout>
)

export const pageQuery = graphql`
  query HomePageQuery {
    headerImage: file(relativePath: { eq: "26871026541_48a8096dd9_o.jpg" }) {
      childImageSharp {
        fluid(maxWidth: 3200) {
          ...GatsbyImageSharpFluid_withWebp
        }
      }
    }
  }
`

IndexPage.propTypes = {
  data: PropTypes.shape({
    headerImage: PropTypes.object.isRequired,
  }).isRequired,
}

export default IndexPage
