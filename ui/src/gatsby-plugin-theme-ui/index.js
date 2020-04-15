export default {
  colors: {
    text: "#333",
    background: "#fff",
    primary: "#0892d0",
    secondary: "#D04608",
    tertiary: "#F98E5F",
    error: "#D04608",
    ok: "#259e06",
    grey: {
      0: "#f8f9f9",
      1: "#ebedee",
      2: "#dee1e3",
      3: "#cfd3d6",
      4: "#bec4c8",
      5: "#acb4b9",
      6: "#97a1a7",
      7: "#7f8a93",
      8: "#5f6e78",
      9: "#374047",
    },
  },
  fonts: {
    body: "Verdana, Geneva, sans-serif",
    heading: "Georgia, serif",
  },
  fontSizes: [12, 14, 16, 18, 24, 32, 48, 64, 72],
  fontWeights: {
    body: 400,
    heading: 900,
    bold: 700,
  },
  text: {
    heading: {
      fontFamily: "heading",
      fontWeight: "heading",
      lineHeight: "heading",
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
      p: {
        fontSize: [2, 3],
      },
      h1: {
        variant: "text.heading",
        fontSize: [5, 6, 7],
      },
      h2: {
        variant: "text.heading",
        fontSize: [4, 5],
      },
    },
  },
}
