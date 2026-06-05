import { useState } from "react";

function App() {
  const [equation, setEquation] = useState("");
  const [result, setResult] = useState(null);

  const analizar = async () => {
    const response = await fetch(
      "http://127.0.0.1:8000/analyze",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          equation,
        }),
      }
    );

    const data = await response.json();
    setResult(data);
  };

  return (
    <div style={{ padding: "30px" }}>
      <h1>Métodos Numéricos</h1>

      <input
        type="text"
        placeholder="Ingrese la ecuación"
        value={equation}
        onChange={(e) => setEquation(e.target.value)}
        style={{
          width: "400px",
          padding: "10px",
        }}
      />

      <br />
      <br />

      <button onClick={analizar}>
        Analizar
      </button>

      {result && (
        <div>
          <h3>Ecuación</h3>
          <p>{result.f_latex}</p>

          <h3>Derivada</h3>
          <p>{result.fp_latex}</p>

          <h3>Excel</h3>
          <p>{result.f_excel}</p>
        </div>
      )}
    </div>
  );
}

export default App;