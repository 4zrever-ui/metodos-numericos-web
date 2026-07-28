import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import Katex from "./Katex.jsx";
import { GX_PRESETS } from "../content/gxPresets.js";
import { compileExpr } from "../lib/evalExpr.js";
import { analyzeG, cobwebPath, iterateG } from "../lib/fixedPoint.js";
import { formatTick, getPlotPalette, gridLines, isoView, makeTransform, niceStep } from "../lib/plotCore.js";

/**
 * Diagrama de telaraña (cobweb) para punto fijo — la pieza estrella de FASE 2.
 *
 * Tres decisiones que vienen de fases anteriores y NO son negociables aquí:
 *
 * 1. **Escala isométrica.** `isoView` fuerza scaleX === scaleY. Sin eso la recta
 *    y = x no se ve a 45° y el rebote contra la diagonal —toda la intuición del
 *    método— se pierde. Es el requisito opuesto al de `FunctionGraph`, que usa
 *    escalas independientes a propósito (arreglo de G1).
 * 2. **Itera en el cliente**, no vía `/method/punto_fijo`: ese endpoint devuelve
 *    `iterations: []` cuando |g'(x₀)| ≥ 1, y la órbita divergente es justo la
 *    que hay que ver dibujada.
 * 3. **Los g(x) vienen de `gxPresets.js`, curados a mano.** El backend sólo sabe
 *    generar x − f/f′, que converge siempre y produce el cobweb menos
 *    ilustrativo posible (hallazgo H1).
 *
 * La divergencia se dibuja y se explica; no se esconde.
 */

const MAX_PASOS = 30;          // tope acordado: suficiente para ver el patrón

// Tolerancia de DIBUJO, no de cálculo. Con el tope de 30 pasos hace falta:
// una convergencia lineal de |g'| ≈ 0.67 (cos x, x²−3x+2) necesita ~40
// iteraciones para ganar 7 cifras, así que con tol 1e-7 el veredicto decía
// "no se ha cerrado" en órbitas que a ojo llevaban rato encima del punto fijo.
// 1e-4 es ~1/100 de píxel en un encuadre típico: invisible. Para el valor con
// la precisión del método está la calculadora, que usa la tolerancia de Excel.
const TOL_DIBUJO = 1e-4;
const ALTO_LIENZO = 420;
const MS_POR_PASO = 420;

// Único color fijo del componente: el rojo de una órbita que se escapa. No sale
// de las variables de tema porque "esto se va" no es una idea que cambie con el
// modo claro/oscuro. Elegido para leerse sobre ambos fondos.
const COLOR_ESCAPE = "#e06c6c";

export default function CobwebGraph() {
  const [idxEc, setIdxEc] = useState(0);
  const preset = GX_PRESETS[idxEc];

  const [gxTexto, setGxTexto] = useState(GX_PRESETS[0].gxs[0].expr);
  const [x0Texto, setX0Texto] = useState(String(GX_PRESETS[0].x0));
  // `null` significa "la órbita entera". No se usa un número grande porque el
  // paso se cuenta en TRAZOS y `MAX_PASOS` cuenta ITERACIONES —y cada iteración
  // son dos trazos—, así que inicializarlo a MAX_PASOS dibujaba media telaraña
  // en las órbitas largas (30 de 60 trazos) sin que nada fallara a la vista.
  const [paso, setPaso] = useState(null);
  const [animando, setAnimando] = useState(false);

  const canvasRef = useRef(null);

  const x0 = Number(x0Texto);
  const x0Valido = Number.isFinite(x0);

  // ── Cálculo ───────────────────────────────────────────────────────────────

  const orbita = useMemo(
    () => (x0Valido
      ? iterateG(gxTexto, x0, { maxIter: MAX_PASOS, tol: TOL_DIBUJO })
      : { status: "escapó", points: [], root: null }),
    [gxTexto, x0, x0Valido]
  );

  const segmentos = useMemo(() => cobwebPath(orbita.points), [orbita]);

  // ¿La g activa es uno de los reordenamientos de la ecuación elegida, o algo
  // que ha escrito el alumno? Cambiar de ecuación ya repone la g del preset,
  // pero al revés —elegir ecuación y luego teclear— la g puede no tener nada
  // que ver con ella, y eso hay que decirlo en pantalla.
  const esPersonalizada = !preset.gxs.some((g) => g.expr === gxTexto);

  // El punto fijo que se marca tiene que ser el de la g QUE SE DIBUJA, no el de
  // la ecuación del selector. Antes se marcaba `preset.raiz` siempre: con una g
  // personalizada eso ponía un punto que ni está sobre la curva ni es el límite
  // de la órbita. Es la misma familia que G3 (estado dependiente sin invalidar).
  const puntoFijo = useMemo(() => {
    const g = compileExpr(gxTexto);
    if (g && preset && Number.isFinite(preset.raiz)) {
      const r = preset.raiz;
      const gr = g(r);
      if (Number.isFinite(gr) && Math.abs(gr - r) < 1e-6) return r;   // la g fija la raíz
    }
    // Si no, el único punto fijo que conocemos con certeza es al que llegó la órbita.
    if (orbita.status === "convergió" && Number.isFinite(orbita.root)) return orbita.root;
    return null;
  }, [gxTexto, preset, orbita]);

  // |g'| se mide en el punto fijo cuando lo conocemos; si no, en x₀, diciendo
  // dónde. El criterio |g'| < 1 es local: prometerlo en el sitio equivocado
  // sería mentir.
  const analisis = useMemo(() => {
    const punto = puntoFijo !== null ? puntoFijo : (x0Valido ? x0 : 0);
    return { ...analyzeG(gxTexto, punto), enPuntoFijo: puntoFijo !== null };
  }, [gxTexto, puntoFijo, x0, x0Valido]);

  const totalPasos = segmentos.length;
  const pasoVisible = paso === null ? totalPasos : Math.min(paso, totalPasos);

  // La animación se DERIVA en vez de sincronizarse con un efecto: cuando la
  // órbita llega al final, `animActiva` pasa a false sola y el efecto limpia su
  // intervalo. Así no hace falta un `setAnimando(false)` dentro del efecto, que
  // es lo que provoca renders en cascada (y lo que React 19 marca como error).
  const animActiva = animando && pasoVisible < totalPasos;

  useEffect(() => {
    if (!animActiva) return undefined;
    const id = setInterval(() => setPaso((p) => Math.min(p + 1, totalPasos)), MS_POR_PASO);
    return () => clearInterval(id);
  }, [animActiva, totalPasos]);

  // ── Encuadre ──────────────────────────────────────────────────────────────

  // Un mismo rango para X e Y: así la diagonal y = x es literalmente la
  // diagonal del recuadro, y el ojo la reconoce sin pensar.
  const rango = useMemo(() => {
    const vals = [];
    if (x0Valido) vals.push(x0);
    if (preset && Number.isFinite(preset.raiz)) vals.push(preset.raiz);

    // Las órbitas que escapan mandan a infinito: se acotan para que un solo
    // salto enorme no aplaste todo lo interesante contra un píxel.
    const base = vals.length ? Math.max(...vals.map(Math.abs), 1) : 1;
    const tope = base * 6 + 4;
    for (const p of orbita.points) {
      if (Number.isFinite(p.x) && Math.abs(p.x) <= tope) vals.push(p.x);
      if (Number.isFinite(p.gx) && Math.abs(p.gx) <= tope) vals.push(p.gx);
    }

    let lo = Math.min(...vals);
    let hi = Math.max(...vals);
    if (!Number.isFinite(lo) || !Number.isFinite(hi)) { lo = -2; hi = 2; }
    if (hi - lo < 1e-6) { lo -= 1.5; hi += 1.5; }
    const margen = (hi - lo) * 0.18;
    return { lo: lo - margen, hi: hi + margen };
  }, [orbita, preset, x0, x0Valido]);

  // ── Dibujo ────────────────────────────────────────────────────────────────

  const dibujar = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const w = canvas.clientWidth;
    const h = canvas.clientHeight;
    if (!w || !h) return;

    const dpr = window.devicePixelRatio || 1;
    canvas.width = Math.round(w * dpr);
    canvas.height = Math.round(h * dpr);
    const ctx = canvas.getContext("2d");
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

    const pal = getPlotPalette(canvas);
    const vista = isoView({ width: w, height: h, xMin: rango.lo, xMax: rango.hi, yMin: rango.lo, yMax: rango.hi });
    const { toScreenX, toScreenY, toMathX, toMathY } = makeTransform(vista);

    ctx.clearRect(0, 0, w, h);
    ctx.fillStyle = pal.bg;
    ctx.fillRect(0, 0, w, h);

    const xMin = toMathX(0), xMax = toMathX(w);
    const yMin = toMathY(h), yMax = toMathY(0);
    const paso1 = niceStep(vista.scaleX, 80);

    // Rejilla
    ctx.strokeStyle = pal.border;
    ctx.lineWidth = 1;
    for (const gx of gridLines(xMin, xMax, paso1)) {
      ctx.beginPath(); ctx.moveTo(toScreenX(gx), 0); ctx.lineTo(toScreenX(gx), h); ctx.stroke();
    }
    for (const gy of gridLines(yMin, yMax, paso1)) {
      ctx.beginPath(); ctx.moveTo(0, toScreenY(gy)); ctx.lineTo(w, toScreenY(gy)); ctx.stroke();
    }

    // Ejes
    ctx.strokeStyle = pal.text;
    ctx.lineWidth = 1.5;
    const ejeY = toScreenX(0), ejeX = toScreenY(0);
    if (ejeY >= 0 && ejeY <= w) { ctx.beginPath(); ctx.moveTo(ejeY, 0); ctx.lineTo(ejeY, h); ctx.stroke(); }
    if (ejeX >= 0 && ejeX <= h) { ctx.beginPath(); ctx.moveTo(0, ejeX); ctx.lineTo(w, ejeX); ctx.stroke(); }

    // Etiquetas numéricas
    ctx.fillStyle = pal.text;
    ctx.font = "11px ui-monospace, Consolas, monospace";
    ctx.textAlign = "center";
    for (const gx of gridLines(xMin, xMax, paso1)) {
      if (Math.abs(gx) < paso1 * 0.01) continue;
      const sy = Math.min(Math.max(ejeX + 14, 12), h - 4);
      ctx.fillText(formatTick(gx, paso1), toScreenX(gx), sy);
    }
    ctx.textAlign = "right";
    for (const gy of gridLines(yMin, yMax, paso1)) {
      if (Math.abs(gy) < paso1 * 0.01) continue;
      const sx = Math.min(Math.max(ejeY - 6, 26), w - 4);
      ctx.fillText(formatTick(gy, paso1), sx, toScreenY(gy) + 4);
    }

    // La diagonal y = x — la referencia contra la que rebota todo
    ctx.strokeStyle = pal.text;
    ctx.lineWidth = 1.5;
    ctx.setLineDash([6, 5]);
    ctx.beginPath();
    ctx.moveTo(toScreenX(rango.lo), toScreenY(rango.lo));
    ctx.lineTo(toScreenX(rango.hi), toScreenY(rango.hi));
    ctx.stroke();
    ctx.setLineDash([]);

    // La curva g(x)
    const g = compileExpr(gxTexto);
    if (g) {
      ctx.strokeStyle = pal.accent;
      ctx.lineWidth = 2.5;
      ctx.beginPath();
      let trazando = false;
      const pasos = Math.round(w * 1.5);
      for (let i = 0; i <= pasos; i++) {
        const mx = xMin + (xMax - xMin) * (i / pasos);
        const my = g(mx);
        if (!Number.isFinite(my) || Math.abs(my) > (rango.hi - rango.lo) * 40) { trazando = false; continue; }
        const sx = toScreenX(mx), sy = toScreenY(my);
        if (!trazando) { ctx.moveTo(sx, sy); trazando = true; } else ctx.lineTo(sx, sy);
      }
      ctx.stroke();
    }

    // El punto fijo (donde g corta la diagonal). Sale de `puntoFijo`, no del
    // preset: con una g personalizada el corte está en otro sitio, y marcar el
    // del preset sería señalar un punto que no está ni sobre la curva.
    if (puntoFijo !== null) {
      const r = puntoFijo;
      ctx.beginPath();
      ctx.arc(toScreenX(r), toScreenY(r), 5, 0, Math.PI * 2);
      ctx.fillStyle = pal.accent;
      ctx.fill();
      ctx.strokeStyle = pal.bg;
      ctx.lineWidth = 2;
      ctx.stroke();
    }

    // La telaraña
    const escapa = orbita.status === "escapó";
    ctx.strokeStyle = escapa ? COLOR_ESCAPE : pal.textStrong;
    ctx.lineWidth = 1.6;
    ctx.beginPath();
    for (let i = 0; i < pasoVisible; i++) {
      const s = segmentos[i];
      ctx.moveTo(toScreenX(s.x1), toScreenY(s.y1));
      ctx.lineTo(toScreenX(s.x2), toScreenY(s.y2));
    }
    ctx.stroke();

    // x₀, de donde arranca todo
    if (x0Valido) {
      ctx.beginPath();
      ctx.arc(toScreenX(x0), toScreenY(0), 4, 0, Math.PI * 2);
      ctx.fillStyle = escapa ? COLOR_ESCAPE : pal.textStrong;
      ctx.fill();
      ctx.font = "bold 12px ui-monospace, Consolas, monospace";
      ctx.textAlign = "center";
      ctx.fillText("x₀", toScreenX(x0), toScreenY(0) + 20);
    }
  }, [rango, gxTexto, orbita, segmentos, pasoVisible, puntoFijo, x0, x0Valido]);

  useEffect(() => { dibujar(); }, [dibujar]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return undefined;
    const ro = new ResizeObserver(() => dibujar());
    ro.observe(canvas);

    // El canvas no hereda el tema: sus colores se leen en cada dibujo, así que
    // hay que repintarlo cuando el tema cambia. Lo correcto es el evento de
    // `matchMedia`, pero un lienzo con los colores del tema anterior es un
    // fallo muy visible, así que se refuerza con `focus` y `visibilitychange`:
    // cubren el caso corriente de cambiar el tema del sistema desde otra
    // aplicación y volver a la pestaña. Son tres escuchas y ningún temporizador.
    const mq = window.matchMedia("(prefers-color-scheme: dark)");
    const repintar = () => dibujar();
    mq.addEventListener("change", repintar);
    window.addEventListener("focus", repintar);
    document.addEventListener("visibilitychange", repintar);

    return () => {
      ro.disconnect();
      mq.removeEventListener("change", repintar);
      window.removeEventListener("focus", repintar);
      document.removeEventListener("visibilitychange", repintar);
    };
  }, [dibujar]);

  // ── Texto del veredicto ───────────────────────────────────────────────────

  const veredicto = (() => {
    if (!x0Valido) return { tono: "aviso", texto: "Escribe un x₀ numérico para lanzar la iteración." };
    switch (orbita.status) {
      case "no-compila":
        return { tono: "aviso", texto: "No consigo interpretar esa g(x). Revisa la sintaxis: se admite ^, sqrt(), cbrt(), exp(), log(), sin(), cos()…" };
      case "convergió":
        return {
          tono: "bien",
          // 4 decimales, no 9: el corte es la tolerancia de dibujo (1e-4) y en
          // convergencia lineal el error real es varias veces el último paso.
          // Prometer nueve cifras aquí sería mentir sobre la precisión.
          texto: `Converge a x ≈ ${orbita.root.toFixed(4)} en ${orbita.points.length} iteraciones. La escalera se cierra sobre el punto fijo. (Para el valor con toda la precisión, la pestaña Calcular.)`,
        };
      case "escapó":
        return {
          tono: "mal",
          texto: "La órbita se escapa: cada rebote la aleja más del punto fijo. Con esta g(x) el método no sirve, por muy correcta que sea el álgebra del despeje.",
        };
      default:
        return {
          tono: "aviso",
          texto: `Tras ${MAX_PASOS} iteraciones no se ha cerrado ni ha escapado: la órbita avanza muy despacio o entra en ciclo.`,
        };
    }
  })();

  // ── Interfaz ──────────────────────────────────────────────────────────────

  // Los reinicios van en los manejadores, no en un efecto: cambiar de g(x) o de
  // x₀ es una acción del alumno, no una sincronización con nada externo.
  const reiniciar = () => { setPaso(null); setAnimando(false); };

  const cambiarEcuacion = (i) => {
    setIdxEc(i);
    setGxTexto(GX_PRESETS[i].gxs[0].expr);
    setX0Texto(String(GX_PRESETS[i].x0));
    reiniciar();
  };

  const cambiarGx = (expr) => { setGxTexto(expr); reiniciar(); };
  const cambiarX0 = (valor) => { setX0Texto(valor); reiniciar(); };

  const alternarAnimacion = () => {
    if (animActiva) { setAnimando(false); return; }
    if (pasoVisible >= totalPasos) setPaso(0);   // al final: reproduce otra vez
    setAnimando(true);
  };

  const gxActual = preset.gxs.find((g) => g.expr === gxTexto) || null;

  return (
    <div className="cobweb">
      <span className="ficha-etiqueta">Demostración interactiva — diagrama de telaraña</span>

      <p className="cobweb-guia">
        La escalera se lee así: sube en vertical desde x hasta la curva g(x), va
        en horizontal hasta la diagonal y = x, y desde ahí vuelve a subir. Si los
        rebotes se cierran sobre el punto donde g corta la diagonal, el método
        converge; si se abren, escapa.
      </p>

      <div className="cobweb-controles">
        <label className="cobweb-campo">
          <span>Ecuación</span>
          <select value={idxEc} onChange={(e) => cambiarEcuacion(Number(e.target.value))}>
            {GX_PRESETS.map((p, i) => (
              <option key={p.equation} value={i}>{p.etiqueta}</option>
            ))}
          </select>
        </label>

        <label className="cobweb-campo">
          <span>x₀</span>
          <input
            type="text"
            inputMode="decimal"
            value={x0Texto}
            onChange={(e) => cambiarX0(e.target.value)}
            className={x0Valido ? undefined : "cobweb-input--malo"}
          />
        </label>
      </div>

      <div className="cobweb-gxs">
        <span className="ficha-etiqueta">Reordenamientos de esta ecuación</span>
        {preset.gxs.map((g) => {
          const a = analyzeG(g.expr, preset.raiz);
          const activo = g.expr === gxTexto;
          return (
            <button
              key={g.expr}
              type="button"
              onClick={() => cambiarGx(g.expr)}
              className={activo ? "cobweb-gx cobweb-gx--activo" : "cobweb-gx"}
            >
              <Katex tex={g.latex} />
              <span className={a.converges ? "cobweb-marca cobweb-marca--atrae" : "cobweb-marca cobweb-marca--repele"}>
                |g′| = {a.ok ? a.absGp.toFixed(3) : "—"} · {a.converges ? "atrae" : "repele"}
              </span>
            </button>
          );
        })}
        {gxActual && <p className="cobweb-nota">{gxActual.nota}</p>}
      </div>

      <label className={esPersonalizada ? "cobweb-campo cobweb-campo--ancho cobweb-campo--activa" : "cobweb-campo cobweb-campo--ancho"}>
        <span>
          {esPersonalizada ? "Tu g(x) — es la que está activa" : "…o escribe la tuya"}
        </span>
        <input type="text" value={gxTexto} onChange={(e) => cambiarGx(e.target.value)} spellCheck="false" />
      </label>

      {esPersonalizada && (
        <p className="cobweb-aviso-personalizada">
          Estás iterando una g(x) tuya, que no es ninguno de los reordenamientos
          de {preset.etiqueta} — por eso ninguno aparece resaltado arriba. El
          punto fijo marcado en el gráfico y el |g′| son los de tu g(x), no los
          de esa ecuación. Elige un reordenamiento para volver a ella.
        </p>
      )}

      <canvas ref={canvasRef} className="cobweb-lienzo" style={{ height: ALTO_LIENZO }} />

      <div className="cobweb-pasos">
        <button type="button" onClick={() => { setAnimando(false); setPaso(Math.max(0, pasoVisible - 1)); }} disabled={pasoVisible === 0}>◀</button>
        <button type="button" onClick={alternarAnimacion} disabled={totalPasos === 0}>
          {animActiva ? "❚❚ pausa" : "▶ animar"}
        </button>
        <button type="button" onClick={() => { setAnimando(false); setPaso(Math.min(totalPasos, pasoVisible + 1)); }} disabled={pasoVisible >= totalPasos}>▶</button>
        <button type="button" onClick={() => { setAnimando(false); setPaso(0); }}>⟲</button>
        <span className="cobweb-contador">
          {totalPasos ? `${pasoVisible} / ${totalPasos} trazos` : "sin órbita"}
        </span>
      </div>

      <p className={`cobweb-veredicto cobweb-veredicto--${veredicto.tono}`}>{veredicto.texto}</p>

      <p className="cobweb-medida">
        {analisis.ok ? (
          <>
            |g′| = <strong>{analisis.absGp.toFixed(4)}</strong>{" "}
            {analisis.enPuntoFijo ? "medido en el punto fijo" : `medido en x = ${analisis.at}`} →{" "}
            {analisis.converges ? "menor que 1, el punto fijo atrae" : "mayor o igual que 1, el punto fijo repele"}.
            {!analisis.enPuntoFijo && " El criterio |g′| < 1 es local: fuera del punto fijo es una pista, no una garantía."}
          </>
        ) : (
          <>No se puede medir |g′| aquí ({analisis.reason}).</>
        )}
      </p>
    </div>
  );
}
