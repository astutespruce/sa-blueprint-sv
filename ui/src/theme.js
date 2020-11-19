import { darken } from '@theme-ui/color'

export default {
  breakpoints: ['600px', '800px', '1600px'],
  colors: {
    text: '#333',
    background: '#fff',
    primary: '#0892d0',
    accent: '#FF8800',
    error: '#D04608',
    ok: '#259e06',
    grey: {
      0: '#f5f5f5',
      1: '#ededed',
      2: '#e1e1e1',
      3: '#d3d3d3',
      4: '#c4c4c4',
      5: '#b3b3b3',
      6: '#a0a0a0',
      7: '#898989',
      8: '#6c6c6c',
      9: '#3f3f3f',
    },
    blue: {
      0: '#eef7fc',
      1: '#e2eff9',
      2: '#cce4f5',
      3: '#b5d8f0',
      4: '#9bcaeb',
      5: '#7dbae5',
      6: '#5aa7de',
      7: '#2d8fd5',
      8: '#006fbe',
      9: '#004170',
    },
  },

  fonts: {
    body: 'Verdana, Georgia, sans-serif',
    heading: 'Verdana, Georgia, sans-serif',
  },
  fontSizes: [12, 14, 16, 18, 24, 32, 48, 64, 72],
  fontWeights: {
    body: 400,
    heading: 900,
    bold: 700,
  },
  layout: {
    container: {
      maxWidth: '960px',
    },
    sidebar: {
      width: ['100%', '320px', '468px', '600px'],
      borderRightWidth: ['0px', '1px'],
      borderRightColor: 'grey.3',
    },
  },
  text: {
    heading: {
      fontFamily: 'heading',
      fontWeight: 'heading',
      lineHeight: 'heading',
    },
    subheading: {
      fontFamily: 'body',
      fontWeight: 'normal',
    },
  },
  lineHeights: {
    body: 1.4,
    heading: 1.2,
  },
  alerts: {
    error: {
      color: '#FFF',
      bg: 'error',
    },
  },
  modal: {
    background: 'grey.9',
  },
  buttons: {
    primary: {
      cursor: 'pointer',
    },
    disabled: {
      cursor: 'not-allowed',
      color: 'grey.7',
      bg: 'blue.1',
    },
    secondary: {
      cursor: 'pointer',
      color: 'grey.9',
      bg: 'grey.1',
    },
    group: {
      cursor: 'pointer',
      bg: 'blue.2',
      py: '0.5em',
      outline: 'none',
      color: 'text',
      '&[data-state="active"]': {
        color: '#FFF',
        bg: 'primary',
      },
      ':not([data-state="active"])': {
        '&:hover': {
          bg: 'blue.3',
        },
      },
      '&:first-of-type': {
        borderRadius: '0.75em 0 0 0.75em',
      },
      '&:not(:first-of-type)': {
        borderRadius: '0 0.75em 0.75em 0',
        borderLeft: '1px solid #FFF',
      },
    },
    close: {
      cursor: 'pointer',
      outline: 'none',
      background: 'none',
      color: 'grey.5',
      '&:hover': { color: 'grey.9' },
    },
    alertClose: {
      cursor: 'pointer',
      outline: 'none',
      background: 'none',
      border: '1px solid',
      borderRadius: '1rem',
      color: '#FFF',
    },
    mobileHeaderClose: {
      cursor: 'pointer',
      outline: 'none',
      background: 'none',
      color: 'grey.2',
    },
    header: {
      cursor: 'pointer',
      border: '1px solid #FFF',
      p: '0.25em 0.5em',
      marginLeft: '1rem',
      '&:hover': {
        bg: darken('primary', 0.05),
      },
    },
  },
  forms: {
    input: {
      outline: 'none',
      border: '1px solid',
      borderColor: 'grey.3',
      borderRadius: '0.25rem',
      py: '0.25rem',
      px: '0.5rem',
      '&:active,&:focus': {
        borderColor: 'primary',
      },
    },
    textarea: {
      fontFamily: 'body',
      fontSize: 1,
      lineHeight: 1.3,
      outline: 'none',
      border: '1px solid',
      borderColor: 'grey.3',
      borderRadius: '0.25rem',
      py: '0.25rem',
      px: '0.5rem',
      '&:active,&:focus': {
        borderColor: 'primary',
      },
    },
  },

  tabs: {
    default: {
      cursor: 'pointer',
      color: 'grey.7',
      bg: 'grey.1',
      borderBottom: '1px solid',
      borderBottomColor: 'grey.6',
      borderTop: '1px solid',
      borderTopColor: 'transparent',
    },
    active: {
      cursor: 'pointer',
      color: 'text',
      bg: '#FFF',
      borderBottom: '1px solid #FFF',
      borderLeft: '1px solid',
      borderLeftColor: 'grey.3',
      borderRight: '1px solid',
      borderRightColor: 'grey.3',
      borderTop: '1px solid',
      borderTopColor: 'grey.3',
    },
    mobile: {
      cursor: 'pointer',
      color: 'grey.1',
      bg: 'primary',
    },
    mobileActive: {
      cursor: 'pointer',
      color: '#FFF',
      bg: darken('primary', 0.05),
    },
  },
  styles: {
    root: {
      height: '100%',
      width: '100%',
      overflowY: 'hidden',
      '#___gatsby': {
        height: '100%',
      },
      '#___gatsby > *': {
        height: '100%',
      },
      fontFamily: 'body',
      fontWeight: 'body',
      lineHeight: 'body',
      a: {
        color: 'primary',
        textDecoration: 'none',
        '&:visited': 'primary',
        '&:hover': {
          textDecoration: 'underline',
        },
      },
      p: {
        fontSize: 2,
        color: 'grey.9',
      },
      ul: {
        margin: 0,
        padding: '0 0 0 1rem',
        color: 'grey.8',
        fontSize: 1,
        '& li + li': {
          mt: '0.5rem',
        },
      },
      h1: {
        variant: 'text.heading',
        fontSize: [5, 6, 7],
      },
      h2: {
        variant: 'text.heading',
        fontSize: [4, 5],
      },
      h3: {
        variant: 'text.heading',
        fontSize: [3, 4],
      },
      h4: {
        fontSize: [2, 3],
        variant: 'text.subheading',
      },
    },
    hr: {
      color: 'grey.3',
      my: '2rem',
      dashed: {
        borderBottom: '1px dashed',
        color: 'grey.3',
        my: '2rem',
      },
      light: {
        color: 'grey.2',
        my: '2rem',
      },
    },
    progress: {
      color: 'primary',
      bg: 'grey.1',
      height: '1rem',
      percent: {
        color: 'primary',
        bg: 'grey.2',
        height: '0.75rem',
      },
    },
  },
}
