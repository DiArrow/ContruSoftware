import React from "react";
import "./index.css"; // estilos globales: body, :root variables

const baseCard = {
  backgroundColor: "#ffffff",
  opacity: 0.95,
  width: "min(90%, 1750px)",
  padding: "32px",
  borderRadius: "24px",
  boxShadow: "0 10px 30px rgba(0, 0, 0, 0.08)",
  position: "relative",
  margin: "10px auto",
  boxSizing: "border-box",
  transition: "box-shadow 0.3s ease",
};

const hoverShadow = { boxShadow: "0 15px 40px rgba(0, 0, 0, 0.12)" };

const styles = {
  cuadroSuperior: {
    ...baseCard,
    height: "var(--cuadro-alto)", 
  },
  cuadroCentral: {
    ...baseCard,
    height: "var(--cuadro-central-alto)",
    border: "1px solid rgba(0, 0, 0, 0.08)",
    marginTop: "70px",    // espacio encima del cuadro
    marginBottom: "30px", // espacio debajo del cuadro 
  },
  cuadroInferior: {
    ...baseCard,
    height: "var(--cuadro-inferior-alto)",
    border: "1px solid rgba(0, 0, 0, 0.08)",
  },
};

function useHover() {
  const [hovered, setHovered] = React.useState(false);
  return {
    hovered,
    onMouseEnter: () => setHovered(true),
    onMouseLeave: () => setHovered(false),
  };
}

function CuadroSuperior({ children }) {
  const { hovered, ...handlers } = useHover();
  return (
    <div style={{ ...styles.cuadroSuperior, ...(hovered ? hoverShadow : {}) }} {...handlers}>
      {children}
    </div>
  );
}

function CuadroCentral({ children }) {
  const { hovered, ...handlers } = useHover();
  return (
    <div style={{ ...styles.cuadroCentral, ...(hovered ? hoverShadow : {}) }} {...handlers}>
      {children}
    </div>
  );
}

function CuadroInferior({ children }) {
  const { hovered, ...handlers } = useHover();
  return (
    <div style={{ ...styles.cuadroInferior, ...(hovered ? hoverShadow : {}) }} {...handlers}>
      {children}
    </div>
  );
}

export default function App() {
  return (
    <>
      <CuadroSuperior>
        <p></p>
      </CuadroSuperior>

      <CuadroCentral>
        <p></p>
      </CuadroCentral>

      <CuadroInferior>
        <p></p>
      </CuadroInferior>
    </>
  );
}
