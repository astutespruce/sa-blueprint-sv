import React from 'react'
import { Flex, Image, Heading } from 'theme-ui'

import { Link } from 'components/link'
import { useMapData } from 'components/data'
import LogoURL from 'images/logo.svg'
import HeaderButtons from './HeaderButtons'
import { useBreakpoints } from './Breakpoints'
import MobileHeader from './mobile/MobileHeader'

const Header = () => {
  const breakpoint = useBreakpoints()
  const isMobile = breakpoint === 0
  const { data, unsetData } = useMapData() || {} // will be null for non-map pages

  return (
    <Flex
      as="header"
      sx={{
        flex: '0 0 auto',
        justifyContent: 'space-between',
        alignItems: 'center',
        py: '0.3rem',
        pl: '0.5rem',
        pr: '1rem',
        bg: 'primary',
        color: '#FFF',
        zIndex: 1,
        boxShadow: '0 2px 6px #333',
      }}
    >
      {isMobile && data !== null ? (
        <MobileHeader {...data} onClose={unsetData} />
      ) : (
        <>
          <Flex
            sx={{
              alignItems: 'center',
            }}
          >
            <Link
              to="/"
              sx={{
                textDecoration: 'none !important',
                lineHeight: 0,
                flex: '0 0 auto',
                display: 'block',
              }}
            >
              <Image
                src={LogoURL}
                alt="South Atlantic Conservation Blueprint - logo"
                width="32"
                height="32"
                sx={{
                  mr: '0.5rem',
                  border: '1px solid #FFF',
                  borderRadius: '2rem',
                }}
              />
            </Link>

            <Link
              to="/"
              sx={{
                textDecoration: 'none !important',
                display: 'block',
                color: '#FFF',
              }}
            >
              <Flex
                sx={{
                  flexWrap: 'wrap',
                  alignItems: ['flex-start', 'flex-start', 'baseline'],
                  flexDirection: ['column', 'column', 'row'],
                }}
              >
                <Heading
                  as="h1"
                  sx={{
                    fontWeight: 'normal',
                    fontSize: [0, 1, 4],
                    lineHeight: 1,
                    margin: '0 0.5rem 0 0',
                    breakInside: 'avoid',
                    flex: '0 1 auto',
                  }}
                >
                  South Atlantic
                </Heading>
                <Heading
                  as="h1"
                  sx={{
                    margin: '0 0.5rem 0 0',
                    fontWeight: 'normal',
                    lineHeight: 1,
                    fontSize: [2, 3, 4],
                    breakInside: 'avoid',
                    flexGrow: 0,
                    flexShrink: 0,
                    flexBasis: ['100%', 'unset'],
                  }}
                >
                  Conservation Blueprint
                </Heading>
                <Heading
                  as="h1"
                  sx={{
                    margin: 0,
                    fontWeight: 'normal',
                    lineHeight: 1,
                    fontSize: [0, 0, 2],
                    breakInside: 'avoid',
                    flexGrow: 0,
                    flexShrink: 0,
                    flexBasis: ['100%', 'unset'],
                  }}
                >
                  Simple Viewer
                </Heading>
              </Flex>
            </Link>
          </Flex>
          {!isMobile && breakpoint >= 1 ? <HeaderButtons /> : null}
        </>
      )}
    </Flex>
  )
}

export default Header
