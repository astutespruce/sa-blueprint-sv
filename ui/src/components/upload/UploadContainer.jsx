import React, { useState, useCallback } from 'react'
import {
  Alert,
  Box,
  Close,
  Container,
  Divider,
  Heading,
  Flex,
  Link,
  Progress,
  Text,
} from 'theme-ui'
import {
  ExclamationTriangle,
  Download,
  CheckCircle,
} from 'emotion-icons/fa-solid'

import { captureException } from 'util/log'
import { uploadFile } from './upload'
import UploadForm from './UploadForm'
import config from '../../../gatsby-config'
import { ThemeContext } from '@emotion/core'
import { useTheme } from 'emotion-theming'

const { contactEmail } = config.siteMetadata

const UploadContainer = () => {
  const [{ reportURL, progress, error, inProgress }, setState] = useState({
    reportURL: null,
    progress: 0,
    inProgress: false,
    error: null, // if error is non-null, it indicates there was an error
  })

  const handleCreateReport = useCallback(async (file, name) => {
    setState((prevState) => ({
      ...prevState,
      inProgress: true,
      progress: 0,
      error: null,
      reportURL: null,
    }))
    try {
      const { error, result } = await uploadFile(file, name, (progress) => {
        setState((prevState) => ({ ...prevState, progress }))
      })

      if (error) {
        console.error(error)
        setState((prevState) => ({
          ...prevState,
          inProgress: false,
          progress: 0,
          error,
        }))
        return
      }

      setState((prevState) => ({
        ...prevState,
        progress: 100,
        inProgress: false,
        reportURL: result,
      }))

      window.location.href = result
    } catch (ex) {
      captureException('File upload failed', ex)
      console.error('Caught unhandled error from uploadFile', ex)

      setState((prevState) => ({
        ...prevState,
        inProgress: false,
        progress: 0,
        error: '', // no meaningful error to show to user, but needs to be non-null
      }))
    }
  }, [])

  const handleClearError = () => {
    setState((prevState) => ({ ...prevState, error: null }))
  }

  return (
    <Container sx={{ py: '2rem' }}>
      {reportURL != null && (
        <Box sx={{ mb: '6rem' }}>
          <Heading as="h2" sx={{ mb: '0.5rem' }}>
            <CheckCircle
              css={{
                height: '1em',
                width: '1em',
                marginRight: '0.5rem',
              }}
            ></CheckCircle>
            All done!
          </Heading>
          <Text>
            Your report is now complete. It should download automatically.
            <br />
            <br />
            You can also click the button below to download your report.
          </Text>

          <Link href={reportURL} target="_blank">
            <Download
              css={{ width: '1rem', height: '1rem', marginRight: '0.5rem' }}
            />
            Download report
          </Link>

          <Divider></Divider>

          <Text>You can also create another report below.</Text>
        </Box>
      )}

      {inProgress ? (
        <>
          <Heading as="h2" sx={{ mb: '0.5rem' }}>
            Creating report...
          </Heading>
          <Flex sx={{ alignItems: 'center' }}>
            <Progress variant="progress" max={100} value={progress}></Progress>
            <Text sx={{ ml: '1rem' }}>{progress}%</Text>
          </Flex>
        </>
      ) : (
        <>
          {error != null && (
            <Alert variant="error" sx={{ mt: '2rem', mb: '4rem', py: '1rem' }}>
              <ExclamationTriangle
                css={{
                  width: '2rem',
                  height: '2rem',
                  margin: '0 1rem 0 0',
                }}
              />
              <Box>
                Uh oh! There was an error!
                <br />
                {error ? (
                  `The server says: ${error}`
                ) : (
                  <>
                    <Text as="span">
                      Please try again. If that doesn't work, try a different
                      file or
                    </Text>{' '}
                    <Link
                      sx={{ color: '#FFF' }}
                      href={`mailto:${contactEmail}`}
                    >
                      Contact Us
                    </Link>
                    .
                  </>
                )}
              </Box>
              <Close ml="auto" mr={-2} onClick={handleClearError} />
            </Alert>
          )}

          <UploadForm
            onFileChange={handleClearError}
            onCreateReport={handleCreateReport}
          />
        </>
      )}
    </Container>
  )
}

export default UploadContainer
