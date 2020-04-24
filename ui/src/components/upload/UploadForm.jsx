import React, { useCallback, useState } from "react"
import PropTypes from "prop-types"
import { Button, Flex, Heading, Input, Text, Divider } from "theme-ui"

import DropZone from "./DropZone"

const UploadForm = ({ onFileChange, onCreateReport }) => {
  const [name, setName] = useState("")
  const [file, setFile] = useState(null)

  const handleDrop = useCallback(file => {
    setFile(file)
    onFileChange()
  }, [])

  const handleInputChange = useCallback(({ target: { value } }) => {
    setName(value)
  }, [])

  const handleResetFile = () => {
    setFile(null)
    onFileChange()
  }

  const handleCreateReport = () => {
    onCreateReport(file, name)
  }

  return (
    <>
      <Heading as="h3" sx={{ mb: "0.5rem" }}>
        Area Name:
      </Heading>
      <Input type="text" onChange={handleInputChange} />

      <Flex
        sx={{
          mt: "2rem",
          mb: "0.5em",
          justifyContent: "space-between",
          alignItems: "center",
        }}
      >
        <div>
          <Heading
            as="h3"
            sx={{
              mb: 0,
            }}
          >
            Choose Area of Interest:
          </Heading>
          <div>{file && <Text>{file.name}</Text>}</div>
        </div>
      </Flex>

      {file === null && <DropZone onDrop={handleDrop} />}

      {file && (
        <>
          <Divider />
          <Flex
            sx={{
              justifyContent: "space-between",
            }}
          >
            <Button variant="secondary" onClick={handleResetFile}>
              Choose a different file
            </Button>

            <Button onClick={handleCreateReport}>Create Report</Button>
          </Flex>
        </>
      )}
    </>
  )
}

UploadForm.propTypes = {
  onFileChange: PropTypes.func.isRequired,
  onCreateReport: PropTypes.func.isRequired,
}

export default UploadForm
