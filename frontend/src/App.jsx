import { useState } from "react";
import "./App.css";

const API = "http://127.0.0.1:8000";

const METHODS = {
  newton:               { label: "Newton-Raphson",    url: "/method/newton",               params: ["x0", "tol"] },
  biseccion:            { label: "Bisección",         url: "/method/biseccion",            params: ["a", "b", "tol"] },
  regula_falsi:         { label: "Regula Falsi",      url: "/method/regula_falsi",         params: ["a", "b", "tol"] },
  punto_fijo:           { label: "Punto Fijo",        url: "/method/punto_fijo",           params: ["x0", "tol"] },
  aitken:               { label: "Aitken (Δ²)",       url: "/method/aitken",               params: ["x0", "tol"] },
  steffensen:           { label: "Steffensen",        url: "/method/steffensen",           params: ["x0", "tol"] },
  secante:              { label: "Secante",           url: "/method/secante",              params: ["x0", "x1", "tol"] },
  von_mises:            { label: "Von Mises",         url: "/method/von_mises",            params: ["x0", "tol"] },
  newton_modificado:    { label: "Newton Modificado", url: "/method/newton_modificado",    params: ["x0", "tol"] },
  newton_segundo_orden: { label: "Newton 2do Orden",  url: "/method/newton_segundo_orden", params: ["x0", "tol"] },
  chebyshev:            { label: "Chebyshev",         url: "/method/chebyshev",            params: ["x0", "tol"] },
  halley:               { label: "Halley",            url: "/method/halley",               params: ["x0", "tol"] },
  super_halley:         { label: "Super Halley",      url: "/method/super_halley",         params: ["x0", "tol"] },
  ostrowsky:            { label: "Ostrowsky",         url: "/method/ostrowsky",            params: ["x0", "tol"] },
};

const PARAM_LABELS = {
  x0:  "x₀ (aprox. inicial)",
  x1:  "x₁ (segunda aprox.)",
  a:   "a (extremo izquierdo)",
  b:   "b (extremo derecho)",
  tol: "Tolerancia",
};

const PARAM_PLACEHOLDERS = {
  x0:  "ej. 2",
  x1:  "ej. 3",
  a:   "ej. 1",
  b:   "ej. 3",
  tol: "0.00001",
};

// Columnas internas que no se muestran en la tabla de iteraciones
const HIDDEN_COLS = new Set(["extra", "converged"]);

function numOrNull(str) {
  if (str === "" || str === null || str === undefined) return null;
  const n = Number(str);
  return isNaN(n) ? null : n;
}

function formatValue(val) {
  if (val === null || val === undefined) return "—";
  if (typeof val === "boolean") return val ? "Sí" : "No";
  if (typeof val === "number") {
    if (Number.isInteger(val)) return val;
    return val.toExponential(6);
  }
  if (typeof val === "object") return JSON.stringify(val);
  return String(val);
}

// ── Descarga de Excel ─────────────────────────────────────────────────────────
async function descargarBlob(url, body, filename) {
  const res = await fetch(`${API}${url}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`Error al generar Excel: ${res.status}`);
  const blob = await res.blob();
  const href = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = href;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(href);
}

// ── Componentes de tabla de iteraciones (flujo individual) ────────────────────
function IterationTable({ iterations }) {
  if (!iterations || iterations.length === 0) return null;
  const cols = Object.keys(iterations[0]).filter((k) => !HIDDEN_COLS.has(k));
  return (
    <div className="table-wrapper">
      <table>
        <thead>
          <tr>{cols.map((col) => <th key={col}>{col}</th>)}</tr>
        </thead>
        <tbody>
          {iterations.map((row, i) => (
            <tr key={i} className={row.converged ? "row-converged" : ""}>
              {cols.map((col) => <td key={col}>{formatValue(row[col])}</td>)}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function Summary({ result, methodLabel }) {
  return (
    <div className="summary">
      <div className="summary-card">
        <span className="summary-label">Método</span>
        <span className="summary-value">{methodLabel}</span>
      </div>
      <div className="summary-card">
        <span className="summary-label">Raíz</span>
        <span className="summary-value mono">
          {result.root != null ? result.root.toPrecision(10) : "—"}
        </span>
      </div>
      <div className="summary-card">
        <span className="summary-label">Iteraciones</span>
        <span className="summary-value">{result.iteration_count}</span>
      </div>
      <div className="summary-card">
        <span className="summary-label">Convergió</span>
        <span className={`summary-value badge ${result.converged ? "badge-ok" : "badge-fail"}`}>
          {result.converged ? "Sí" : "No"}
        </span>
      </div>
      {result.final_error_pct != null && (
        <div className="summary-card">
          <span className="summary-label">Error final</span>
          <span className="summary-value mono">{result.final_error_pct.toExponential(4)}%</span>
        </div>
      )}
    </div>
  );
}

// ── Tabla comparativa (flujo "Resolver todos") ────────────────────────────────
function ComparisonTable({ results, equation }) {
  const [downloading, setDownloading] = useState(null); // key del método descargando

  const handleExcelSingle = async (methodKey) => {
    setDownloading(methodKey);
    try {
      await descargarBlob(
        "/excel/single",
        { equation, method_key: methodKey },
        `metodos_numericos_${methodKey}.xlsx`
      );
    } catch (e) {
      alert(e.message);
    } finally {
      setDownloading(null);
    }
  };

  return (
    <div className="table-wrapper comparison-table-wrapper">
      <table className="comparison-table">
        <thead>
          <tr>
            <th className="col-method">Método</th>
            <th className="col-root">Raíz</th>
            <th className="col-iter">Iter.</th>
            <th className="col-error">Error final</th>
            <th className="col-conv">Convergió</th>
            <th className="col-excel">Excel</th>
          </tr>
        </thead>
        <tbody>
          {results.map((r) => {
            const label = METHODS[r.method]?.label ?? r.method;
            const applicable = r.applicable !== false;
            return (
              <tr
                key={r.method}
                className={
                  !applicable
                    ? "row-na"
                    : r.converged
                    ? "row-converged"
                    : "row-noconv"
                }
              >
                <td className="col-method">{label}</td>
                <td className="col-root mono">
                  {r.root != null ? r.root.toPrecision(8) : "—"}
                </td>
                <td className="col-iter">
                  {r.iteration_count ?? "—"}
                </td>
                <td className="col-error mono">
                  {r.final_error_pct != null
                    ? r.final_error_pct.toExponential(3) + "%"
                    : "—"}
                </td>
                <td className="col-conv">
                  {!applicable ? (
                    <span className="badge badge-na" title={r.reason}>N/A</span>
                  ) : r.converged ? (
                    <span className="badge badge-ok">Sí</span>
                  ) : (
                    <span className="badge badge-fail" title={r.reason}>No</span>
                  )}
                </td>
                <td className="col-excel">
                  <button
                    className="btn-excel-single"
                    onClick={() => handleExcelSingle(r.method)}
                    disabled={downloading === r.method}
                    title={`Descargar Excel — ${label}`}
                  >
                    {downloading === r.method ? "…" : "↓ xlsx"}
                  </button>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

// ── App principal ─────────────────────────────────────────────────────────────
export default function App() {
  // Estado del flujo individual (sin cambios)
  const [equation, setEquation]         = useState("x^3 - 2*x - 5");
  const [method, setMethod]             = useState("newton");
  const [manualParams, setManualParams] = useState({});
  const [showParams, setShowParams]     = useState(false);
  const [result, setResult]             = useState(null);
  const [error, setError]               = useState(null);
  const [loading, setLoading]           = useState(false);

  // Estado del flujo comparativo — independiente, no toca nada de arriba
  const [allResults, setAllResults]     = useState(null);
  const [loadingAll, setLoadingAll]     = useState(false);
  const [errorAll, setErrorAll]         = useState(null);
  const [downloadingAll, setDownloadingAll] = useState(false);

  const currentParamKeys = METHODS[method].params;

  const handleMethodChange = (e) => {
    setMethod(e.target.value);
    setManualParams({});
    setResult(null);
    setError(null);
  };

  const handleParamChange = (key, val) => {
    setManualParams((prev) => ({ ...prev, [key]: val }));
  };

  // ── Resolver individual ───────────────────────────────────────────────────
  const resolver = async () => {
    if (!equation.trim()) {
      setError("Ingresa una ecuación antes de resolver.");
      setResult(null);
      return;
    }
    setError(null);
    setResult(null);
    setLoading(true);
    try {
      const { url } = METHODS[method];
      const body = { equation: equation.trim() };
      for (const key of currentParamKeys) {
        const val = numOrNull(manualParams[key]);
        if (val !== null) body[key] = val;
      }
      const res = await fetch(`${API}${url}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      if (!res.ok) {
        const detail = await res.json().catch(() => ({}));
        throw new Error(
          detail?.detail ? JSON.stringify(detail.detail) : `Error del servidor: ${res.status}`
        );
      }
      const data = await res.json();
      if (!data || typeof data !== "object") throw new Error("Respuesta inválida del backend.");
      if (data.applicable === false) {
        setError(`Método no aplicable: ${data.reason}`);
        return;
      }
      if (!data.converged) {
        setError(`El método no convergió en ${data.iteration_count} iteraciones.`);
      }
      setResult(data);
    } catch (e) {
      setError(
        e instanceof TypeError && e.message.includes("fetch")
          ? "No se pudo conectar con el backend. ¿Está corriendo uvicorn?"
          : e.message
      );
    } finally {
      setLoading(false);
    }
  };

  // ── Resolver todos ────────────────────────────────────────────────────────
  const resolverTodos = async () => {
    if (!equation.trim()) {
      setErrorAll("Ingresa una ecuación antes de resolver.");
      return;
    }
    setErrorAll(null);
    setAllResults(null);
    setLoadingAll(true);
    try {
      const res = await fetch(`${API}/method/all`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ equation: equation.trim() }),
      });
      if (!res.ok) {
        const detail = await res.json().catch(() => ({}));
        throw new Error(
          detail?.detail ? JSON.stringify(detail.detail) : `Error del servidor: ${res.status}`
        );
      }
      const data = await res.json();
      setAllResults(data.results);
    } catch (e) {
      setErrorAll(
        e instanceof TypeError && e.message.includes("fetch")
          ? "No se pudo conectar con el backend. ¿Está corriendo uvicorn?"
          : e.message
      );
    } finally {
      setLoadingAll(false);
    }
  };

  // ── Descargar Excel completo ──────────────────────────────────────────────
  const descargarExcelAll = async () => {
    if (!equation.trim()) return;
    setDownloadingAll(true);
    try {
      await descargarBlob(
        "/excel/all",
        { equation: equation.trim() },
        "metodos_numericos_todos.xlsx"
      );
    } catch (e) {
      setErrorAll(e.message);
    } finally {
      setDownloadingAll(false);
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>Métodos Numéricos</h1>
        <p className="subtitle">Resolución de ecuaciones no lineales</p>
      </header>

      {/* ── Bloque 1: Formulario principal ── */}
      <section className="form-section">
        <div className="form-group form-group--equation">
          <label htmlFor="equation">Ecuación f(x) = 0</label>
          <input
            id="equation"
            type="text"
            value={equation}
            onChange={(e) => setEquation(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && resolver()}
            placeholder="ej. x^3 - 2*x - 5"
            spellCheck={false}
            autoComplete="off"
          />
        </div>

        <div className="form-group">
          <label htmlFor="method">Método</label>
          <select id="method" value={method} onChange={handleMethodChange}>
            <optgroup label="Intervalo">
              <option value="biseccion">Bisección</option>
              <option value="regula_falsi">Regula Falsi</option>
            </optgroup>
            <optgroup label="Punto Fijo">
              <option value="punto_fijo">Punto Fijo</option>
              <option value="aitken">Aitken (Δ²)</option>
              <option value="steffensen">Steffensen</option>
            </optgroup>
            <optgroup label="Derivada">
              <option value="newton">Newton-Raphson</option>
              <option value="von_mises">Von Mises</option>
              <option value="secante">Secante</option>
            </optgroup>
            <optgroup label="Familia Newton">
              <option value="newton_modificado">Newton Modificado</option>
              <option value="newton_segundo_orden">Newton 2do Orden</option>
              <option value="chebyshev">Chebyshev</option>
              <option value="halley">Halley</option>
              <option value="super_halley">Super Halley</option>
              <option value="ostrowsky">Ostrowsky</option>
            </optgroup>
          </select>
        </div>

        <div className="btn-group">
          <button className="btn-resolver" onClick={resolver} disabled={loading}>
            {loading ? "Calculando…" : "Resolver"}
          </button>
          <button
            className="btn-todos"
            onClick={resolverTodos}
            disabled={loadingAll}
          >
            {loadingAll ? "Calculando…" : "Resolver todos"}
          </button>
        </div>
      </section>

      {/* ── Bloque 2: Parámetros manuales ── */}
      <section className="params-section">
        <button
          className="params-toggle"
          onClick={() => setShowParams((v) => !v)}
        >
          {showParams ? "▲" : "▼"} Parámetros manuales{" "}
          <span className="params-toggle-hint">(opcional — dejar vacío usa valores automáticos)</span>
        </button>
        {showParams && (
          <div className="params-grid">
            {currentParamKeys.map((key) => (
              <div className="form-group" key={key}>
                <label htmlFor={`param-${key}`}>{PARAM_LABELS[key]}</label>
                <input
                  id={`param-${key}`}
                  type="number"
                  step="any"
                  value={manualParams[key] ?? ""}
                  onChange={(e) => handleParamChange(key, e.target.value)}
                  placeholder={PARAM_PLACEHOLDERS[key]}
                />
              </div>
            ))}
          </div>
        )}
      </section>

      {/* ── Bloque 3: Error flujo individual ── */}
      {error && (
        <div className="error-box">
          <span className="error-icon">⚠</span> {error}
        </div>
      )}

      {/* ── Bloque 4: Resumen flujo individual ── */}
      {result && <Summary result={result} methodLabel={METHODS[method].label} />}

      {/* ── Bloque 5: Tabla de iteraciones flujo individual ── */}
      {result?.iterations?.length > 0 && (
        <section className="iterations-section">
          <h2>Tabla de iteraciones</h2>
          <IterationTable iterations={result.iterations} />
        </section>
      )}

      {/* ── Bloque 6: Error flujo comparativo ── */}
      {errorAll && (
        <div className="error-box error-box--all">
          <span className="error-icon">⚠</span> {errorAll}
        </div>
      )}

      {/* ── Bloque 7: Tabla comparativa + descarga Excel ── */}
      {allResults && (
        <section className="comparison-section">
          <div className="comparison-header">
            <h2>Comparativa — 14 métodos</h2>
            <button
              className="btn-excel-all"
              onClick={descargarExcelAll}
              disabled={downloadingAll}
            >
              {downloadingAll ? "Generando…" : "↓ Descargar Excel completo"}
            </button>
          </div>
          <ComparisonTable results={allResults} equation={equation.trim()} />
        </section>
      )}
    </div>
  );
}
