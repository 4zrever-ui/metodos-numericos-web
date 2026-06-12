import React, { useState } from "react";
import "./App.css";

const API = "http://127.0.0.1:8000";

const METHODS = {
  newton:               { label: "Newton-Raphson",    url: "/method/newton",               params: ["x0", "tol"] },
  biseccion:            { label: "Bisección",         url: "/method/biseccion",            params: ["a", "b", "tol"] },
  regula_falsi:         { label: "Regula Falsi",      url: "/method/regula_falsi",         params: ["a", "b", "tol"] },
  punto_fijo:           { label: "Punto Fijo",        url: "/method/punto_fijo",           params: ["x0", "gx", "tol"] },
  aitken:               { label: "Aitken (Δ²)",       url: "/method/aitken",               params: ["x0", "gx", "tol"] },
  steffensen:           { label: "Steffensen",        url: "/method/steffensen",           params: ["x0", "gx", "tol"] },
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
  gx:  "g(x) manual (opcional)",
};

const PARAM_PLACEHOLDERS = {
  x0:  "ej. 2",
  x1:  "ej. 3",
  a:   "ej. 1",
  b:   "ej. 3",
  tol: "0.00001",
  gx:  "ej. (x+7)/(x+1)",
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

// ── Explicación clara cuando un método no aplica / no converge ────────────────
async function fetchDiagnose(equation, methodKey, applicable) {
  try {
    const res = await fetch(`${API}/diagnose`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ equation, method_key: methodKey, applicable }),
    });
    if (!res.ok) throw new Error();
    return await res.json();
  } catch {
    return {
      has_real_roots: null,
      title: applicable ? "El método no convergió" : "Este método no se puede aplicar",
      body: "No se encontró una raíz para esta ecuación con este método.",
      suggestion: "Prueba con otra ecuación, otro método o cambia los valores iniciales.",
    };
  }
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

// ── Aviso claro cuando no hay raíz (no aplica / no converge) ──────────────────
function MethodNotice({ notice }) {
  if (!notice) return null;
  const noRoots = notice.has_real_roots === false;
  return (
    <div className={`notice-card ${noRoots ? "notice-card--info" : "notice-card--warn"}`}>
      <div className="notice-head">
        <span className="notice-icon">{noRoots ? "ⓘ" : "⚠"}</span>
        <span className="notice-title">{notice.title}</span>
      </div>
      <p className="notice-body">{notice.body}</p>
      {notice.suggestion && (
        <div className="notice-hint">
          <span className="notice-hint-label">Sugerencia</span>
          {notice.suggestion}
        </div>
      )}
    </div>
  );
}

// ── Tabla comparativa (flujo "Resolver todos") ────────────────────────────────
function ComparisonTable({ results, equation, manualParams = {} }) {
  const [downloading, setDownloading] = useState(null); // key del método descargando

  const handleExcelSingle = async (methodKey) => {
    setDownloading(methodKey);
    try {
      await descargarBlob(
        "/excel/single",
        { equation, method_key: methodKey, ...manualParams },
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


// ── Gráfico interactivo de f(x) ───────────────────────────────────────────
function FunctionGraph({ equation, roots = [] }) {
  const canvasRef = React.useRef(null);
  const stateRef  = React.useRef({ ox: 0, oy: 0, scale: 60, dragging: false, lastX: 0, lastY: 0 });

  // Parse and evaluate f(x) safely
  const evalF = React.useCallback((x) => {
    try {
      // Convert Python-style to JS
      let expr = equation
        .replace(/\*\*/g, "^POW^")   // mark ** first
        .replace(/\^POW\^/g, "**")    // restore as JS **
        .replace(/([0-9a-zA-Z_)])(\s*)(\()/g, "$1*$3")  // implicit mult: 2(x) → 2*(x)
        .replace(/\bsin\b/g, "Math.sin")
        .replace(/\bcos\b/g, "Math.cos")
        .replace(/\btan\b/g, "Math.tan")
        .replace(/\blog\b/g, "Math.log")
        .replace(/\bexp\b/g, "Math.exp")
        .replace(/\bsqrt\b/g, "Math.sqrt")
        .replace(/\babs\b/g, "Math.abs")
        .replace(/\bpi\b/g, "Math.PI")
        .replace(/\be\b/g, "Math.E")
        .replace(/\^/g, "**");
      // eslint-disable-next-line no-new-func
      return Function("x", `"use strict"; return (${expr})`)(x);
    } catch { return NaN; }
  }, [equation]);

  const draw = React.useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    const W = canvas.width, H = canvas.height;
    const { ox, oy, scale } = stateRef.current;

    ctx.clearRect(0, 0, W, H);

    // Background
    ctx.fillStyle = "#1a1a2e";
    ctx.fillRect(0, 0, W, H);

    const toScreenX = (x) => ox + x * scale;
    const toScreenY = (y) => oy - y * scale;
    const toMathX   = (sx) => (sx - ox) / scale;

    // Grid
    const xMin = toMathX(0), xMax = toMathX(W);
    const yMin = (oy - H) / scale, yMax = oy / scale;
    // gridStep adaptativo: mínimo 70px entre líneas, pasos 1/2/5 × 10^n
    const minPx = 70;
    const rawStep = minPx / scale;
    const mag = Math.pow(10, Math.floor(Math.log10(rawStep)));
    const norm = rawStep / mag;
    let gridStep;
    if (norm <= 1)      gridStep = 1 * mag;
    else if (norm <= 2) gridStep = 2 * mag;
    else if (norm <= 5) gridStep = 5 * mag;
    else                gridStep = 10 * mag;

    ctx.strokeStyle = "#353560";
    ctx.lineWidth = 1;
    for (let gx = Math.ceil(xMin / gridStep) * gridStep; gx <= xMax; gx += gridStep) {
      ctx.beginPath(); ctx.moveTo(toScreenX(gx), 0); ctx.lineTo(toScreenX(gx), H); ctx.stroke();
    }
    for (let gy = Math.ceil(yMin / gridStep) * gridStep; gy <= yMax; gy += gridStep) {
      ctx.beginPath(); ctx.moveTo(0, toScreenY(gy)); ctx.lineTo(W, toScreenY(gy)); ctx.stroke();
    }

    // Tick marks on axes
    ctx.strokeStyle = "#6060a0";
    ctx.lineWidth = 1.5;
    const tickSize = 5;
    for (let gx = Math.ceil(xMin / gridStep) * gridStep; gx <= xMax; gx += gridStep) {
      if (Math.abs(gx) < gridStep * 0.01) continue;
      const sx = toScreenX(gx);
      const sy = Math.min(Math.max(oy, 0), H);
      ctx.beginPath(); ctx.moveTo(sx, sy - tickSize); ctx.lineTo(sx, sy + tickSize); ctx.stroke();
    }
    for (let gy = Math.ceil(yMin / gridStep) * gridStep; gy <= yMax; gy += gridStep) {
      if (Math.abs(gy) < gridStep * 0.01) continue;
      const sx = Math.min(Math.max(ox, 0), W);
      const sy = toScreenY(gy);
      ctx.beginPath(); ctx.moveTo(sx - tickSize, sy); ctx.lineTo(sx + tickSize, sy); ctx.stroke();
    }

    // Axes
    ctx.strokeStyle = "#7070b0";
    ctx.lineWidth = 2;
    // Y axis
    if (ox >= 0 && ox <= W) {
      ctx.beginPath(); ctx.moveTo(ox, 0); ctx.lineTo(ox, H); ctx.stroke();
    }
    // X axis
    if (oy >= 0 && oy <= H) {
      ctx.beginPath(); ctx.moveTo(0, oy); ctx.lineTo(W, oy); ctx.stroke();
    }

    // Axis labels — bright and readable
    ctx.font = "bold 12px monospace";

    // Helper: draw label with dark background pill
    const drawLabel = (text, x, y, align) => {
      ctx.textAlign = align;
      const tw = ctx.measureText(text).width;
      const pad = 3;
      let bx = x;
      if (align === "center") bx = x - tw / 2;
      else if (align === "right") bx = x - tw;
      ctx.fillStyle = "rgba(20,20,45,0.75)";
      ctx.fillRect(bx - pad, y - 12, tw + pad * 2, 16);
      ctx.fillStyle = "#c0c0ff";
      ctx.fillText(text, x, y);
    };

    // fmtNum: muestra exactamente los decimales que necesita según gridStep
    const fmtNum = (v) => {
      if (Math.abs(v) < gridStep * 0.01) return "0";
      // Cuántos decimales necesita el paso actual
      const decimals = Math.max(0, -Math.floor(Math.log10(gridStep)));
      return v.toFixed(decimals);
    };

    ctx.textAlign = "center";
    for (let gx = Math.ceil(xMin / gridStep) * gridStep; gx <= xMax; gx += gridStep) {
      if (Math.abs(gx) < gridStep * 0.01) continue;
      const sx = toScreenX(gx), sy = Math.min(Math.max(oy + 16, 16), H - 6);
      drawLabel(fmtNum(gx), sx, sy, "center");
    }
    for (let gy = Math.ceil(yMin / gridStep) * gridStep; gy <= yMax; gy += gridStep) {
      if (Math.abs(gy) < gridStep * 0.01) continue;
      const sx = Math.min(Math.max(ox - 8, 4), W - 4), sy = toScreenY(gy) + 4;
      drawLabel(fmtNum(gy), sx, sy, "right");
    }

    // Origin label
    if (ox >= 0 && ox <= W && oy >= 0 && oy <= H) {
      drawLabel("0", Math.min(Math.max(ox - 8, 4), W - 4), Math.min(Math.max(oy + 16, 16), H - 6), "right");
    }

    // Curve f(x)
    ctx.strokeStyle = "#a78bfa";
    ctx.lineWidth = 2.5;
    ctx.beginPath();
    let penDown = false;
    let prevY = null;
    const steps = W * 1.5;
    for (let i = 0; i <= steps; i++) {
      const mx = xMin + (xMax - xMin) * (i / steps);
      const my = evalF(mx);
      const sy = toScreenY(my);
      if (!isFinite(my) || Math.abs(my) > 1e6 || (prevY !== null && Math.abs(sy - prevY) > H * 2)) {
        penDown = false; prevY = null; continue;
      }
      if (!penDown) { ctx.moveTo(toScreenX(mx), sy); penDown = true; }
      else ctx.lineTo(toScreenX(mx), sy);
      prevY = sy;
    }
    ctx.stroke();

    // X-axis crossing line (y=0)
    if (oy >= 0 && oy <= H) {
      ctx.strokeStyle = "#ffffff22";
      ctx.lineWidth = 1;
      ctx.setLineDash([4, 4]);
      ctx.beginPath(); ctx.moveTo(0, oy); ctx.lineTo(W, oy);
      ctx.stroke();
      ctx.setLineDash([]);
    }

    // Roots
    roots.forEach((r) => {
      const sx = toScreenX(r), sy = toScreenY(0);
      if (sx < -20 || sx > W + 20) return;

      // Vertical dashed line at root
      ctx.strokeStyle = "#f87171aa";
      ctx.lineWidth = 1;
      ctx.setLineDash([4, 3]);
      ctx.beginPath(); ctx.moveTo(sx, 0); ctx.lineTo(sx, H); ctx.stroke();
      ctx.setLineDash([]);

      // Dot on x-axis
      ctx.beginPath();
      ctx.arc(sx, sy, 6, 0, Math.PI * 2);
      ctx.fillStyle = "#f87171";
      ctx.fill();
      ctx.strokeStyle = "#fff";
      ctx.lineWidth = 1.5;
      ctx.stroke();

      // Label with background pill
      ctx.font = "bold 13px monospace";
      ctx.textAlign = "center";
      const rootText = "x≈" + r.toPrecision(6);
      const rtw = ctx.measureText(rootText).width;
      const rty = Math.max(sy - 18, 18);
      ctx.fillStyle = "rgba(20,10,10,0.82)";
      ctx.fillRect(sx - rtw/2 - 6, rty - 13, rtw + 12, 20);
      ctx.fillStyle = "#ff9090";
      ctx.fillText(rootText, sx, rty);
    });

    // Hover tooltip sobre raíz
    const hoverRoot = stateRef.current.hoverRoot;
    if (hoverRoot !== null && hoverRoot !== undefined) {
      const sx = toScreenX(hoverRoot);
      const sy = toScreenY(0);
      const tipText = "x = " + hoverRoot.toPrecision(8).replace(/\.?0+$/, "");
      ctx.font = "bold 13px monospace";
      ctx.textAlign = "center";
      const tw = ctx.measureText(tipText).width;
      const tx = Math.min(Math.max(sx, tw/2 + 10), W - tw/2 - 10);
      const ty = Math.max(sy - 30, 24);
      // background
      ctx.fillStyle = "rgba(10,10,30,0.92)";
      ctx.fillRect(tx - tw/2 - 8, ty - 16, tw + 16, 22);
      // border
      ctx.strokeStyle = "#f87171";
      ctx.lineWidth = 1.5;
      ctx.strokeRect(tx - tw/2 - 8, ty - 16, tw + 16, 22);
      // text
      ctx.fillStyle = "#ffd0d0";
      ctx.fillText(tipText, tx, ty);
    }
  }, [equation, roots, evalF]);

  // Redraw on equation/roots change
  React.useEffect(() => { draw(); }, [draw]);

  // Resize observer + wheel con passive:false para evitar scroll de página
  React.useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ro = new ResizeObserver(() => {
      canvas.width  = canvas.offsetWidth;
      canvas.height = canvas.offsetHeight;
      draw();
    });
    ro.observe(canvas);
    canvas.width  = canvas.offsetWidth;
    canvas.height = canvas.offsetHeight;
    draw();

    const onWheel = (e) => {
      e.preventDefault();
      const rect = canvas.getBoundingClientRect();
      const mx = e.clientX - rect.left;
      const my = e.clientY - rect.top;
      const s = stateRef.current;
      const factor = e.deltaY < 0 ? 1.15 : 1 / 1.15;
      s.ox = mx - (mx - s.ox) * factor;
      s.oy = my - (my - s.oy) * factor;
      s.scale *= factor;
      draw();
    };
    canvas.addEventListener("wheel", onWheel, { passive: false });

    return () => { ro.disconnect(); canvas.removeEventListener("wheel", onWheel); };
  }, [draw]);

  // Drag
  const onMouseDown = (e) => {
    const s = stateRef.current;
    s.dragging = true; s.lastX = e.clientX; s.lastY = e.clientY;
  };
  const onMouseMove = (e) => {
    const s = stateRef.current;
    if (s.dragging) {
      s.ox += e.clientX - s.lastX;
      s.oy += e.clientY - s.lastY;
      s.lastX = e.clientX; s.lastY = e.clientY;
      draw();
      return;
    }
    const canvas = canvasRef.current;
    if (!canvas) return;
    const rect = canvas.getBoundingClientRect();
    const mx = e.clientX - rect.left;
    const my = e.clientY - rect.top;
    const toScreenX = (x) => s.ox + x * s.scale;
    const toScreenY = (y) => s.oy - y * s.scale;
    const HOVER_PX = 20; // px de proximidad al eje X

    let hit = null;

    // 1) Hover sobre punto rojo de raíz calculada
    for (const r of roots) {
      const sx = toScreenX(r);
      const sy = toScreenY(0);
      const dist = Math.sqrt((mx - sx) ** 2 + (my - sy) ** 2);
      if (dist < HOVER_PX) { hit = r; break; }
    }

    // 2) Si el cursor está cerca del eje X, buscar cruce real de f(x)=0 evaluando la curva
    if (hit === null && Math.abs(my - toScreenY(0)) < HOVER_PX) {
      const mathX = (mx - s.ox) / s.scale;
      // Buscar signo cambia alrededor de mathX en ventana pequeña
      const window = HOVER_PX / s.scale;
      const steps = 80;
      let bestRoot = null, bestDist = Infinity;
      for (let i = 0; i < steps; i++) {
        const xa = mathX - window + (2 * window * i / steps);
        const xb = mathX - window + (2 * window * (i + 1) / steps);
        const fa = evalF(xa), fb = evalF(xb);
        if (!isFinite(fa) || !isFinite(fb)) continue;
        if (fa * fb <= 0) {
          // Bisección rápida para afinar el cruce
          let lo = xa, hi = xb;
          for (let k = 0; k < 30; k++) {
            const mid = (lo + hi) / 2;
            if (evalF(lo) * evalF(mid) <= 0) hi = mid; else lo = mid;
          }
          const root = (lo + hi) / 2;
          const d = Math.abs(mathX - root);
          if (d < bestDist) { bestDist = d; bestRoot = root; }
        }
      }
      if (bestRoot !== null) hit = bestRoot;
    }

    s.hoverRoot = hit;
    canvas.style.cursor = hit !== null ? "crosshair" : "grab";
    draw();
  };
  const onMouseUp = () => { stateRef.current.dragging = false; };

  // Reset view
  const resetView = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    stateRef.current.ox = canvas.width / 2;
    stateRef.current.oy = canvas.height / 2;
    stateRef.current.scale = 60;
    draw();
  };

  // Center on roots
  const centerRoots = () => {
    if (!roots.length) return;
    const canvas = canvasRef.current;
    const cx = roots.reduce((a, b) => a + b, 0) / roots.length;
    stateRef.current.ox = canvas.width / 2 - cx * stateRef.current.scale;
    stateRef.current.oy = canvas.height / 2;
    draw();
  };

  return (
    <div style={{ position: "relative", width: "100%", height: "320px", borderRadius: "10px", overflow: "hidden", border: "1px solid #3a3a5a", marginBottom: "1.5rem" }}>
      <canvas
        ref={canvasRef}
        style={{ width: "100%", height: "100%", cursor: "grab", display: "block" }}
        onMouseDown={onMouseDown}
        onMouseMove={onMouseMove}
        onMouseUp={onMouseUp}
        onMouseLeave={onMouseUp}
      />
      <div style={{ position: "absolute", top: 10, right: 10, display: "flex", gap: "6px" }}>
        <button onClick={resetView}  style={btnStyle}>⌂ Reset</button>
        {roots.length > 0 && <button onClick={centerRoots} style={btnStyle}>● Raíces</button>}
      </div>
      <div style={{ position: "absolute", bottom: 8, left: 10, color: "#7070a0", fontSize: "11px", pointerEvents: "none" }}>
        Scroll para zoom · Drag para mover
      </div>
    </div>
  );
}

const btnStyle = {
  background: "#2a2a4a", border: "1px solid #4a4a7a", color: "#a0a0c0",
  borderRadius: "6px", padding: "4px 10px", cursor: "pointer", fontSize: "12px",
};

// ── App principal ─────────────────────────────────────────────────────────────
export default function App() {
  // Estado del flujo individual (sin cambios)
  const [equation, setEquation]         = useState("x^3 - 2*x - 5");
  const [method, setMethod]             = useState("newton");
  const [manualParams, setManualParams] = useState({});
  const [showParams, setShowParams]     = useState(false);
  const [result, setResult]             = useState(null);
  const [error, setError]               = useState(null);
  const [notice, setNotice]             = useState(null);
  const [loading, setLoading]           = useState(false);

  // Parámetros automáticos calculados por el backend (para mostrar como placeholder)
  const [autoParams, setAutoParams]     = useState({});

  // Raíces para el gráfico (se actualizan con /params y con cada resolve)
  const [graphRoots, setGraphRoots]     = useState([]);

  // Pide al backend los parámetros auto cada vez que cambia la ecuación
  const fetchAutoParams = async (eq) => {
    if (!eq.trim()) { setAutoParams({}); return; }
    try {
      const res = await fetch(`${API}/params`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ equation: eq.trim() }),
      });
      if (!res.ok) return;
      const data = await res.json();
      if (!data.error) {
        setAutoParams(data);
        if (data.roots) setGraphRoots(data.roots);
      }
    } catch { /* silencioso */ }
  };

  // Estado del flujo comparativo — independiente, no toca nada de arriba
  const [allResults, setAllResults]     = useState(null);
  const [allNotice, setAllNotice]       = useState(null);
  const [loadingAll, setLoadingAll]     = useState(false);
  const [errorAll, setErrorAll]         = useState(null);
  const [downloadingAll, setDownloadingAll] = useState(false);

  const currentParamKeys = METHODS[method].params;

  const handleMethodChange = (e) => {
    setMethod(e.target.value);
    setManualParams({});
    setResult(null);
    setError(null);
    setNotice(null);
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
    setNotice(null);
    setResult(null);
    setLoading(true);
    try {
      const { url } = METHODS[method];
      const body = { equation: equation.trim() };
      for (const key of currentParamKeys) {
        if (key === "gx") {
          const s = (manualParams[key] ?? "").trim();
          if (s) body[key] = s;
        } else {
          const val = numOrNull(manualParams[key]);
          if (val !== null) body[key] = val;
        }
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
      const applicable = data.applicable !== false;
      if (!applicable || !data.converged) {
        const diag = await fetchDiagnose(equation.trim(), method, applicable);
        setNotice(diag);
        setResult(applicable ? data : null); // si no aplica, no hay tabla útil
        return;
      }
      setResult(data);
      setShowParams(true); // abrir panel para mostrar valores usados
      // Actualizar raíces en el gráfico si el método convergió
      if (data.root != null) {
        setGraphRoots((prev) => {
          const already = prev.some((r) => Math.abs(r - data.root) < 1e-6);
          return already ? prev : [...prev, data.root];
        });
      }
      // Mostrar los valores automáticos usados en los inputs
      if (data.params_used) {
        const filled = {};
        for (const key of METHODS[method].params) {
          const v = data.params_used[key];
          if (v !== undefined && v !== null) filled[key] = String(v);
        }
        setManualParams((prev) => ({ ...filled, ...prev }));
      }
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
    setAllNotice(null);
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
      const algunoConverge = (data.results || []).some((r) => r.converged);
      if (!algunoConverge) {
        const diag = await fetchDiagnose(equation.trim(), "", true);
        setAllNotice(diag.has_real_roots === false ? diag : null);
      }
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
        { equation: equation.trim(), ...manualParams },
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
            onChange={(e) => { setEquation(e.target.value); fetchAutoParams(e.target.value); }}
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

      {/* ── Gráfico de f(x) ── */}
      {equation.trim() && (
        <section style={{ padding: "0 0 0 0" }}>
          <FunctionGraph equation={equation.trim()} roots={graphRoots} />
        </section>
      )}

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
                  type={key === "gx" ? "text" : "number"}
                  step={key === "gx" ? undefined : "any"}
                  value={manualParams[key] ?? ""}
                  onChange={(e) => handleParamChange(key, e.target.value)}
                  placeholder={
                    autoParams[key] !== undefined
                      ? `auto: ${autoParams[key]}`
                      : (key === "x1" && autoParams["x0_alt"] !== undefined)
                        ? `auto: ${autoParams["x0_alt"]}`
                        : PARAM_PLACEHOLDERS[key]
                  }
                  spellCheck={false}
                  autoComplete="off"
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

      {/* ── Bloque 3b: Aviso claro (no aplica / no converge) ── */}
      {notice && <MethodNotice notice={notice} />}

      {/* ── Bloque 4: Resumen flujo individual ── */}
      {result && <Summary result={result} methodLabel={METHODS[method].label} />}

      {/* ── Bloque 5: Tabla de iteraciones flujo individual ── */}
      {result?.iterations?.length > 0 && (
        <section className="iterations-section">
          <div className="iterations-header">
            <h2>Tabla de iteraciones</h2>
            <button
              className="btn-excel-individual"
              onClick={async () => {
                try {
                  const mk = method === "newton" ? "newton_raphson"
                           : method === "newton_segundo_orden" ? "newton_2do_orden"
                           : method;
                  await descargarBlob(
                    "/excel/single",
                    { equation: equation.trim(), method_key: mk, ...manualParams },
                    `metodos_numericos_${mk}.xlsx`
                  );
                } catch (e) { alert(e.message); }
              }}
            >
              ↓ Descargar Excel
            </button>
          </div>
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
          {allNotice && <MethodNotice notice={allNotice} />}
          <ComparisonTable results={allResults} equation={equation.trim()} manualParams={manualParams} />
        </section>
      )}
    </div>
  );
}
