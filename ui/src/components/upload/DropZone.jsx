import React, { useCallback, useState } from "react"
import { useDropzone } from "react-dropzone"
import { Alert, Box, Flex, Heading, Text } from "theme-ui"
import { transparentize } from "@theme-ui/color"
import { Download, ExclamationTriangle } from "emotion-icons/fa-solid"

const MAXSIZE_MB = 100

const DropZone = () => {
  const [invalidFiles, setInvalidFiles] = useState(null)

  const onDrop = useCallback((acceptedFiles, rejectedFiles) => {
    console.log("files", acceptedFiles, "rejected: ", rejectedFiles)

    if (rejectedFiles) {
      setInvalidFiles(rejectedFiles.map(d => d.name).join(", "))
    }
  }, [])
  const {
    getRootProps,
    getInputProps,
    isDragActive,
    isDragAccept,
    isDragReject,
  } = useDropzone({
    onDrop,
    accept: "application/zip",
    maxSize: MAXSIZE_MB * 1e6,
  })

  let color = "grey.5"
  if (isDragAccept) {
    color = "ok"
  } else if (isDragReject) {
    color = "error"
  }

  return (
    <Flex
      sx={{
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      <Flex
        {...getRootProps({ isDragActive, isDragAccept, isDragReject })}
        sx={{
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          p: "2rem",
          maxWidth: "640px",
          my: "1rem",
          mx: "auto",
          cursor: "pointer",
          outline: "none",
          borderWidth: "2px",
          borderStyle: "dashed",
          borderRadius: "1rem",
          borderColor: color,
          backgroundColor: transparentize(color, 0.9),
        }}
      >
        <input {...getInputProps()} />
        <Download width="2rem" height="2rem" css={{ marginBottom: "1rem" }} />
        <Heading as="h3" sx={{ mb: "1rem" }}>
          Drop your zip file here
        </Heading>
        <Text as="p" sx={{ color: "grey.7", textAlign: "center", fontSize: 1 }}>
          Zip file must contain all associated files for a shapefile (.shp,
          .prj, .dbf) or file geodatabase (.gdb).
          <br />
          Max size: {MAXSIZE_MB} mb.
        </Text>
      </Flex>

      {invalidFiles !== null && (
        <Alert variant="error" sx={{ maxWidth: "640px" }}>
          <ExclamationTriangle
            width="1.5rem"
            height="1.5rem"
            css={{ marginRight: "1rem", flex: "0 0 auto" }}
          />{" "}
          Not supported: {invalidFiles}
        </Alert>
      )}
    </Flex>
  )
}

export default DropZone
