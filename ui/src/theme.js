import { darken } from "@theme-ui/color"

export default {
  breakpoints: ["600px", "800px", "1600px"],
  colors: {
    text: "#333",
    background: "#fff",
    primary: "#0892d0",
    secondary: "#D04608",
    tertiary: "#F98E5F",
    error: "#D04608",
    ok: "#259e06",
    grey: {
      0: "#f9f9f9",
      1: "#ededed",
      2: "#e1e1e1",
      3: "#d3d3d3",
      4: "#c4c4c4",
      5: "#b3b3b3",
      6: "#a0a0a0",
      7: "#898989",
      8: "#6c6c6c",
      9: "#3f3f3f",
    },
    blue: {
      0: "#f6fafd",
      1: "#e2eff9",
      2: "#cce4f5",
      3: "#b5d8f0",
      4: "#9bcaeb",
      5: "#7dbae5",
      6: "#5aa7de",
      7: "#2d8fd5",
      8: "#006fbe",
      9: "#004170",
    },
  },

  fonts: {
    body: "Verdana, Geneva, sans-serif",
    heading: "Verdana, Geneva, sans-serif",
  },
  fontSizes: [12, 14, 16, 18, 24, 32, 48, 64, 72],
  fontWeights: {
    body: 400,
    heading: 900,
    bold: 700,
  },
  layout: {
    container: {
      maxWidth: "960px",
    },
    sidebar: {
      width: ["100%", "320px", "468px", "600px"],
      borderRightWidth: ["0px", "1px"],
      borderRightColor: "grey.3",
    },
  },
  text: {
    heading: {
      fontFamily: "heading",
      fontWeight: "heading",
      lineHeight: "heading",
    },
    subheading: {
      fontFamily: "body",
      fontWeight: "normal",
    },
  },
  lineHeights: {
    body: 1.4,
    heading: 1.2,
  },
  alerts: {
    error: {
      color: "#FFF",
      bg: "error",
    },
  },
  modal: {
    background: "grey.9",
  },
  buttons: {
    primary: {
      cursor: "pointer",
    },
    secondary: {
      cursor: "pointer",
      color: "grey.9",
      bg: "grey.1",
    },
    close: {
      cursor: "pointer",
      outline: "none",
      background: "none",
      color: "grey.5",
      "&:hover": { color: "grey.9" },
    },
    mobileHeaderClose: {
      cursor: "pointer",
      outline: "none",
      background: "none",
      color: "grey.2",
    },
    header: {
      cursor: "pointer",
      border: "1px solid #FFF",
      p: "0.25em 0.5em",
      marginLeft: "1rem",
      "&:hover": {
        bg: darken("primary", 0.05),
      },
    },
  },
  forms: {
    input: {
      outline: "none",
      borderColor: "grey.3",
      "&:active,&:focus": {
        borderColor: "primary",
      },
    },
  },
  progress: {
    color: "primary",
    bg: "grey.2",
    height: "1rem",
  },
  tabs: {
    default: {
      cursor: "pointer",
      color: "grey.7",
      bg: "grey.1",
      borderBottom: "1px solid",
      borderBottomColor: "grey.6",
      borderTop: "1px solid",
      borderTopColor: "transparent",
    },
    active: {
      cursor: "pointer",
      color: "text",
      bg: "#FFF",
      borderBottom: "1px solid #FFF",
      borderLeft: "1px solid",
      borderLeftColor: "grey.3",
      borderRight: "1px solid",
      borderRightColor: "grey.3",
      borderTop: "1px solid",
      borderTopColor: "grey.3",
    },
    mobile: {
      cursor: "pointer",
      color: "grey.1",
      bg: "primary",
    },
    mobileActive: {
      cursor: "pointer",
      color: "#FFF",
      bg: darken("primary", 0.05),
    },
  },
  styles: {
    root: {
      height: "100vh",
      overflowY: "hidden",
      "#___gatsby": {
        height: "100%",
      },
      "#___gatsby > *": {
        height: "100%",
      },
      fontFamily: "body",
      fontWeight: "body",
      lineHeight: "body",
      a: {
        color: "primary",
        "&:visited": "primary",
      },
      p: {
        fontSize: 2,
        color: "grey.8",
      },
      ul: {
        margin: 0,
        padding: "0 0 0 1rem",
        color: "grey.8",
        fontSize: 1,
        "& li + li": {
          mt: "0.5rem",
        },
      },
      h1: {
        variant: "text.heading",
        fontSize: [5, 6, 7],
      },
      h2: {
        variant: "text.heading",
        fontSize: [4, 5],
      },
      h3: {
        variant: "text.heading",
        fontSize: [3, 4],
      },
      h4: {
        fontSize: [2, 3],
        variant: "text.subheading",
      },
    },
    hr: {
      color: "grey.3",
      my: "2rem",
    },
  },
}
