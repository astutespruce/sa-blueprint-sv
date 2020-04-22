import React, { useState, useCallback } from "react"
import { Button, Container, Heading, Input, Progress } from "theme-ui"

import uploadFile from "./upload"
import DropZone from "./DropZone"

const UploadContainer = () => {
  const [name, setName] = useState("")
  const [file, setFile] = useState(null)

  const handleDrop = useCallback(file => {
    setFile(file)

    // TODO: show filename to user, make them click an upload button
    // const request = uploadFile(file)
    // request
    //   .then(success => {
    //     console.log("Success uploading file", success)
    //   })
    //   .catch(error => {
    //     console.error("Caught error uploading", error)
    //   })

    //       // TODO: show progress and handle errors
  }, [])

  const handleInputChange = useCallback(({ target: { value } }) => {
    setName(value)
  }, [])

  return (
    <Container>
      <Heading as="h3" sx={{ mb: "0.5rem" }}>
        Area Name:
      </Heading>
      <Input type="text" onChange={handleInputChange} />

      <Heading
        as="h3"
        sx={{
          mt: "2rem",
          mb: "0.5em",
          display: "flex",
          justifyContent: "space-between",
        }}
      >
        <div>Upload Area of Interest:</div>
        {file && <div>{file.name}</div>}
      </Heading>

      <DropZone onDrop={handleDrop} />

      {/* <Button>Upload</Button> */}
    </Container>
  )
}

export default UploadContainer
