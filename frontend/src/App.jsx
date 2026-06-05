function App() {
  return (
    <div style={{ padding: "30px" }}>
      <h1>Métodos Numéricos</h1>

      <p>Generador automático de plantillas Excel</p>

      <input
        type="text"
        placeholder="Ingrese la ecuación"
        style={{
          width: "400px",
          padding: "10px",
          marginTop: "20px",
        }}
      />

      <br />
      <br />

      <button>Analizar</button>
    </div>
  );
}

export default App;