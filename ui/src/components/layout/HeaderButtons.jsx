import React from 'react'
import { Box, Button, Flex } from 'theme-ui'
import { FileAlt } from '@emotion-icons/fa-regular'

import { Link } from 'components/link'

const HeaderButtons = () => (
  <Flex
    sx={{ alignItems: 'center', flex: '0 0 auto' }}
    title="Upload your area of interest to create a detailed report including maps and analyses."
  >
    <Link to="/custom_report">
      <Button
        variant="header"
        sx={{
          display: 'flex',
          alignItems: 'center',
        }}
      >
        <FileAlt size="1em" />
        <Box sx={{ marginLeft: '0.5rem', display: ['none', 'none', 'block'] }}>
          Upload Shapefile
        </Box>
      </Button>
    </Link>
  </Flex>
)

export default HeaderButtons
