export default {
  breakpoints: ["600px", "800px", "1200px"],
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
      width: ["100%", "320px", "468px"],
      borderRight: ["none", "1px solid"],
      borderRightColor: "grey.5",
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
    },
  },
  forms: {
    input: {
      outline: "none",
      borderColor: "grey.7",
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
      h4: {
        variant: "text.subheading",
      },
    },
    hr: {
      color: "grey.3",
      my: "2rem",
    },
  },
}