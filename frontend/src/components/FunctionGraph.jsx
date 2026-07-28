import React from "react";

import { getPlotPalette } from "../lib/plotCore.js";

/**
 * Grafico interactivo de f(x) con auto-encuadre, zoom y arrastre.
 *
 * EXTRAIDO de `CalcularPage` en FASE 3 (paso 2) SIN tocar una sola linea de su
 * cuerpo: es un movimiento literal, para que la bateria de G1 pueda demostrar
 * que sigue encuadrando exactamente igual. Lo pedia VISION Â§3, que da por
 * reutilizable este grafico en Practicar; hasta ahora era privado del archivo
 * que carga los nueve bugs cerrados (G1-G9), asi que no habia forma de usarlo.
 *
 * Sigue con los colores oscuros cableados. Adaptarlo al tema es el paso 2b,
 * aparte a proposito: G1 se mide POR EL COLOR de la curva, y cambiar la paleta
 * en el mismo movimiento habria hecho imposible probar que el traslado fue fiel.
 */
// ── Gráfico interactivo de f(x) ───────────────────────────────────────────
function FunctionGraph({ equation, roots = [] }) {
  const canvasRef = React.useRef(null);
  const stateRef  = React.useRef({ ox: 0, oy: 0, scaleX: 60, scaleY: 60, dragging: false, lastX: 0, lastY: 0 });

  // Parse and evaluate f(x) safely
  const evalF = React.useCallback((x) => {
    try {
      // Convert Python-style to JS
      let expr = equation
        .replace(/\*\*/g, "^POW^")   // mark ** first
        .replace(/\^POW\^/g, "**")    // restore as JS **
        .replace(/([0-9)])(\s*)(\()/g, "$1*$3")  // implicit mult: 2(x) → 2*(x); NO tras letra (rompía sin( cos( tan( …)
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

  // Auto-encuadre adaptativo (C-adaptada): escalas X/Y INDEPENDIENTES. Todo client-side.
  const computeAutoView = React.useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const W = canvas.width, H = canvas.height;
    if (!W || !H) return;

    // Rango X: centrado en las raíces (si hay) con margen; si no, default centrado.
    let xMin, xMax;
    if (roots.length) {
      const lo = Math.min(...roots), hi = Math.max(...roots);
      const c = (lo + hi) / 2;
      const half = Math.max((hi - lo) / 2, 1.5) * 1.4;
      xMin = c - half; xMax = c + half;
    } else {
      xMin = -5; xMax = 5;
    }

    // Rango Y: muestrear f y ajustar; recorte BURDO de extremos (asíntotas/explosiones).
    let yLo = Infinity, yHi = -Infinity;
    const N = 240;
    for (let i = 0; i <= N; i++) {
      const x = xMin + (xMax - xMin) * (i / N);
      const y = evalF(x);
      if (!isFinite(y) || Math.abs(y) > 1e4) continue;   // recorte burdo
      if (y < yLo) yLo = y;
      if (y > yHi) yHi = y;
    }
    if (!isFinite(yLo) || !isFinite(yHi)) { yLo = -5; yHi = 5; }   // todo recortado
    yLo = Math.min(yLo, 0); yHi = Math.max(yHi, 0);               // eje X siempre visible
    if (yHi - yLo < 1e-6) { yLo -= 1; yHi += 1; }                 // casi constante
    const padY = (yHi - yLo) * 0.15;
    yLo -= padY; yHi += padY;

    const s = stateRef.current;
    s.scaleX = W / (xMax - xMin);
    s.scaleY = H / (yHi - yLo);
    s.ox = -xMin * s.scaleX;
    s.oy = yHi * s.scaleY;
  }, [evalF, roots]);

  const draw = React.useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    const W = canvas.width, H = canvas.height;
    const { ox, oy, scaleX, scaleY } = stateRef.current;

    ctx.clearRect(0, 0, W, H);

    // Paleta del tema (paso 2b). Se lee en cada dibujo, no se cachea: cambiar de
    // claro a oscuro no remonta el componente, sólo cambia las variables CSS.
    const pal = getPlotPalette(canvas);
    // El rojo de las raíces es el ÚNICO color fijo, igual que el de la órbita que
    // escapa en la telaraña: "aquí está la raíz" no es una idea que cambie con el
    // tema, y este tono se lee sobre los dos fondos.
    const ROJO = "#e0555a";

    // Background
    ctx.fillStyle = pal.bg;
    ctx.fillRect(0, 0, W, H);

    const toScreenX = (x) => ox + x * scaleX;
    const toScreenY = (y) => oy - y * scaleY;
    const toMathX   = (sx) => (sx - ox) / scaleX;

    // Grid
    const xMin = toMathX(0), xMax = toMathX(W);
    const yMin = (oy - H) / scaleY, yMax = oy / scaleY;
    // gridStep adaptativo POR EJE (escalas X/Y independientes): mín 70px, pasos 1/2/5 × 10^n
    const minPx = 70;
    const niceStep = (s) => {
      const raw = minPx / s;
      const mag = Math.pow(10, Math.floor(Math.log10(raw)));
      const norm = raw / mag;
      if (norm <= 1) return 1 * mag;
      if (norm <= 2) return 2 * mag;
      if (norm <= 5) return 5 * mag;
      return 10 * mag;
    };
    const gridStepX = niceStep(scaleX);
    const gridStepY = niceStep(scaleY);

    // Rejilla, marcas y ejes se derivan del color de texto con distinta opacidad:
    // así la jerarquía (rejilla < marcas < ejes) se mantiene en los dos temas sin
    // elegir seis colores a mano.
    ctx.strokeStyle = pal.text;
    ctx.globalAlpha = 0.22;
    ctx.lineWidth = 1;
    for (let gx = Math.ceil(xMin / gridStepX) * gridStepX; gx <= xMax; gx += gridStepX) {
      ctx.beginPath(); ctx.moveTo(toScreenX(gx), 0); ctx.lineTo(toScreenX(gx), H); ctx.stroke();
    }
    for (let gy = Math.ceil(yMin / gridStepY) * gridStepY; gy <= yMax; gy += gridStepY) {
      ctx.beginPath(); ctx.moveTo(0, toScreenY(gy)); ctx.lineTo(W, toScreenY(gy)); ctx.stroke();
    }
    ctx.globalAlpha = 1;

    // Tick marks on axes
    ctx.strokeStyle = pal.text;
    ctx.globalAlpha = 0.6;
    ctx.lineWidth = 1.5;
    const tickSize = 5;
    for (let gx = Math.ceil(xMin / gridStepX) * gridStepX; gx <= xMax; gx += gridStepX) {
      if (Math.abs(gx) < gridStepX * 0.01) continue;
      const sx = toScreenX(gx);
      const sy = Math.min(Math.max(oy, 0), H);
      ctx.beginPath(); ctx.moveTo(sx, sy - tickSize); ctx.lineTo(sx, sy + tickSize); ctx.stroke();
    }
    for (let gy = Math.ceil(yMin / gridStepY) * gridStepY; gy <= yMax; gy += gridStepY) {
      if (Math.abs(gy) < gridStepY * 0.01) continue;
      const sx = Math.min(Math.max(ox, 0), W);
      const sy = toScreenY(gy);
      ctx.beginPath(); ctx.moveTo(sx - tickSize, sy); ctx.lineTo(sx + tickSize, sy); ctx.stroke();
    }

    ctx.globalAlpha = 1;

    // Axes
    ctx.strokeStyle = pal.text;
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

    // Helper: pastilla del color del FONDO bajo el texto, para que los números
    // del eje se lean por encima de la rejilla en cualquiera de los dos temas.
    const drawLabel = (text, x, y, align) => {
      ctx.textAlign = align;
      const tw = ctx.measureText(text).width;
      const pad = 3;
      let bx = x;
      if (align === "center") bx = x - tw / 2;
      else if (align === "right") bx = x - tw;
      ctx.fillStyle = pal.bg;
      ctx.globalAlpha = 0.8;
      ctx.fillRect(bx - pad, y - 12, tw + pad * 2, 16);
      ctx.globalAlpha = 1;
      ctx.fillStyle = pal.text;
      ctx.fillText(text, x, y);
    };

    // fmtNum: muestra exactamente los decimales que necesita según gridStep
    const fmtNum = (v, step) => {
      if (Math.abs(v) < step * 0.01) return "0";
      // Cuántos decimales necesita el paso de ese eje
      const decimals = Math.max(0, -Math.floor(Math.log10(step)));
      return v.toFixed(decimals);
    };

    ctx.textAlign = "center";
    for (let gx = Math.ceil(xMin / gridStepX) * gridStepX; gx <= xMax; gx += gridStepX) {
      if (Math.abs(gx) < gridStepX * 0.01) continue;
      const sx = toScreenX(gx), sy = Math.min(Math.max(oy + 16, 16), H - 6);
      drawLabel(fmtNum(gx, gridStepX), sx, sy, "center");
    }
    for (let gy = Math.ceil(yMin / gridStepY) * gridStepY; gy <= yMax; gy += gridStepY) {
      if (Math.abs(gy) < gridStepY * 0.01) continue;
      const sx = Math.min(Math.max(ox - 8, 4), W - 4), sy = toScreenY(gy) + 4;
      drawLabel(fmtNum(gy, gridStepY), sx, sy, "right");
    }

    // Origin label
    if (ox >= 0 && ox <= W && oy >= 0 && oy <= H) {
      drawLabel("0", Math.min(Math.max(ox - 8, 4), W - 4), Math.min(Math.max(oy + 16, 16), H - 6), "right");
    }

    // Curve f(x) — el acento del tema: f(x) es la protagonista, mismo principio
    // que fijó el director para la telaraña.
    ctx.strokeStyle = pal.accent;
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
      ctx.strokeStyle = pal.text;
      ctx.globalAlpha = 0.15;
      ctx.lineWidth = 1;
      ctx.setLineDash([4, 4]);
      ctx.beginPath(); ctx.moveTo(0, oy); ctx.lineTo(W, oy);
      ctx.stroke();
      ctx.setLineDash([]);
      ctx.globalAlpha = 1;
    }

    // Roots
    roots.forEach((r) => {
      const sx = toScreenX(r), sy = toScreenY(0);
      if (sx < -20 || sx > W + 20) return;

      // Vertical dashed line at root
      ctx.strokeStyle = ROJO;
      ctx.globalAlpha = 0.7;
      ctx.lineWidth = 1;
      ctx.setLineDash([4, 3]);
      ctx.beginPath(); ctx.moveTo(sx, 0); ctx.lineTo(sx, H); ctx.stroke();
      ctx.setLineDash([]);
      ctx.globalAlpha = 1;

      // Dot on x-axis. El anillo va del color del FONDO —antes era blanco fijo—
      // para que separe el disco de la curva en los dos temas.
      ctx.beginPath();
      ctx.arc(sx, sy, 6, 0, Math.PI * 2);
      ctx.fillStyle = ROJO;
      ctx.fill();
      ctx.strokeStyle = pal.bg;
      ctx.lineWidth = 1.5;
      ctx.stroke();

      // Label with background pill
      ctx.font = "bold 13px monospace";
      ctx.textAlign = "center";
      const rootText = "x≈" + r.toPrecision(6);
      const rtw = ctx.measureText(rootText).width;
      const rty = Math.max(sy - 18, 18);
      ctx.fillStyle = pal.bg;
      ctx.globalAlpha = 0.85;
      ctx.fillRect(sx - rtw/2 - 6, rty - 13, rtw + 12, 20);
      ctx.globalAlpha = 1;
      ctx.fillStyle = ROJO;
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
      ctx.fillStyle = pal.bg;
      ctx.globalAlpha = 0.94;
      ctx.fillRect(tx - tw/2 - 8, ty - 16, tw + 16, 22);
      ctx.globalAlpha = 1;
      // border
      ctx.strokeStyle = ROJO;
      ctx.lineWidth = 1.5;
      ctx.strokeRect(tx - tw/2 - 8, ty - 16, tw + 16, 22);
      // text
      ctx.fillStyle = pal.textStrong;
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
      computeAutoView();
      draw();
    });
    ro.observe(canvas);
    canvas.width  = canvas.offsetWidth;
    canvas.height = canvas.offsetHeight;
    computeAutoView();
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
      s.scaleX *= factor;
      s.scaleY *= factor;
      draw();
    };
    canvas.addEventListener("wheel", onWheel, { passive: false });

    // El lienzo no hereda el tema: sus colores se leen en cada dibujo, así que
    // hay que repintarlo cuando el tema cambia. Lo correcto es el evento de
    // `matchMedia`; se refuerza con `focus` y `visibilitychange` porque cubren
    // el caso corriente de cambiar el tema del sistema desde otra aplicación y
    // volver a la pestaña. Mismo patrón —y misma razón— que en `CobwebGraph`.
    const mq = window.matchMedia("(prefers-color-scheme: dark)");
    const repintar = () => draw();
    mq.addEventListener("change", repintar);
    window.addEventListener("focus", repintar);
    document.addEventListener("visibilitychange", repintar);

    return () => {
      ro.disconnect();
      canvas.removeEventListener("wheel", onWheel);
      mq.removeEventListener("change", repintar);
      window.removeEventListener("focus", repintar);
      document.removeEventListener("visibilitychange", repintar);
    };
  }, [draw, computeAutoView]);

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
    const toScreenX = (x) => s.ox + x * s.scaleX;
    const toScreenY = (y) => s.oy - y * s.scaleY;
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
      const mathX = (mx - s.ox) / s.scaleX;
      // Buscar signo cambia alrededor de mathX en ventana pequeña
      const window = HOVER_PX / s.scaleX;
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
    computeAutoView();   // Reset = reencuadra a la función actual
    draw();
  };

  // Center on roots
  const centerRoots = () => {
    if (!roots.length) return;
    const canvas = canvasRef.current;
    const cx = roots.reduce((a, b) => a + b, 0) / roots.length;
    stateRef.current.ox = canvas.width / 2 - cx * stateRef.current.scaleX;
    stateRef.current.oy = canvas.height / 2;
    draw();
  };

  return (
    <div style={{ position: "relative", width: "100%", height: "320px", borderRadius: "10px", overflow: "hidden", border: "1px solid var(--border)", marginBottom: "1.5rem" }}>
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
      <div style={{ position: "absolute", bottom: 8, left: 10, color: "var(--text)", fontSize: "11px", pointerEvents: "none" }}>
        Scroll para zoom · Drag para mover
      </div>
    </div>
  );
}

const btnStyle = {
  background: "var(--bg)", border: "1px solid var(--border)", color: "var(--text-h)",
  borderRadius: "6px", padding: "4px 10px", cursor: "pointer", fontSize: "12px",
};

// El export va al final a proposito: asi el cuerpo movido queda intacto,
// linea por linea, y la bateria de G1 puede demostrar que encuadra igual.
export default FunctionGraph;
