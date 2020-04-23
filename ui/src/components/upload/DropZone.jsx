import React, { useCallback, useState } from "react"
import PropTypes from "prop-types"
import { useDropzone } from "react-dropzone"
import { Alert, Box, Flex, Heading, Text } from "theme-ui"
import { transparentize } from "@theme-ui/color"
import { Download, ExclamationTriangle } from "emotion-icons/fa-solid"

const MAXSIZE_MB = 100

const DropZone = ({ onDrop }) => {
  const [error, setError] = useState(null)

  /**
   * Validate the files provided by the user.
   * They must be only one file, must be right MIME type and be less than the
   * maximum size.
   */
  const handleDrop = useCallback((acceptedFiles, rejectedFiles) => {
    console.log("files", acceptedFiles, "rejected: ", rejectedFiles)

    if (rejectedFiles && rejectedFiles.length > 0) {
      if (rejectedFiles.length > 1) {
        setError(
          `Multiple files not allowed: ${rejectedFiles
            .map(d => d.name)
            .join(", ")}`
        )
        return
      }

      const { name, size } = rejectedFiles[0]
      const mb = size / 1e6
      console.log("mb", mb)
      if (mb >= MAXSIZE_MB) {
        setError(
          `File is too large: ${name} (${Math.round(mb).toLocaleString()} MB)`
        )
        return
      }

      setError(`File type supported: ${name}`)
      return
    }

    if (acceptedFiles && acceptedFiles.length > 0) {
      setError(null)
      onDrop(acceptedFiles[0])
    }
  }, [])

  const {
    getRootProps,
    getInputProps,
    isDragActive,
    isDragAccept,
    isDragReject,
  } = useDropzone({
    onDrop: handleDrop,
    accept: "application/zip",
    maxSize: MAXSIZE_MB * 1e6,
    multiple: false,
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
          width: "100%",
          p: "2rem",
          //   mt:
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
          <br />
          Max size: {MAXSIZE_MB} MB.
        </Text>
      </Flex>

      {error !== null && (
        <Alert variant="error" sx={{ maxWidth: "640px" }}>
          <ExclamationTriangle
            width="1.5rem"
            height="1.5rem"
            css={{ marginRight: "1rem", flex: "0 0 auto" }}
          />
          {error}
        </Alert>
      )}
    </Flex>
  )
}

DropZone.propTypes = {
  onDrop: PropTypes.func.isRequired,
}

export default DropZone
