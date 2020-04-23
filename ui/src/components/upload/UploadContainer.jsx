import React, { useState, useCallback } from "react"
import {
  Alert,
  Box,
  Close,
  Container,
  Heading,
  Flex,
  Progress,
  Text,
} from "theme-ui"
import { ExclamationTriangle } from "emotion-icons/fa-solid"

import uploadFile from "./upload"
import UploadForm from "./UploadForm"

const UploadContainer = () => {
  const [{ progress, hasError, inProgress }, setState] = useState({
    progress: 0,
    inProgress: false,
    hasError: false,
  })

  const handleCreateReport = useCallback((file, name) => {
    console.log("Inputs", name, file.name)
    setState(prevState => ({ ...prevState, inProgress: true, hasError: false }))
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

  const handleClearError = () => {
    setState(prevState => ({ ...prevState, hasError: false }))
  }

  return (
    <Container sx={{ py: "2rem" }}>
      {inProgress ? (
        <>
          <Heading as="h3" sx={{ mb: "0.5rem" }}>
            Creating report...
          </Heading>
          <Flex sx={{ alignItems: "center" }}>
            <Progress variant="progress" max={100} value={progress}></Progress>
            <Text sx={{ ml: "1rem" }}>{progress}%</Text>
          </Flex>
        </>
      ) : (
        <>
          {hasError && (
            <Alert variant="error" sx={{ mb: "2rem" }}>
              <ExclamationTriangle
                css={{
                  width: "1rem",
                  height: "1rem",
                  margin: "0 0.5rem 0 0",
                }}
              />
              Uh oh! There was an error! Please try again. If that doesn't work,
              try a different file.
              <Close ml="auto" mr={-2} onClick={handleClearError} />
            </Alert>
          )}

          <UploadForm onCreateReport={handleCreateReport} />
        </>
      )}
    </Container>
  )
}

export default UploadContainer
