/**
 * Piezas puras y compartidas para dibujar en canvas: conversión mundo↔pantalla,
 * pasos de rejilla, formato de etiquetas, encuadre isométrico y paleta de tema.
 *
 * Sin React y sin canvas: todo aquí es aritmética o lectura de CSS, para que se
 * pueda probar sin montar nada.
 *
 * Nace en FASE 2 para la telaraña. `FunctionGraph` (en `CalcularPage`) tiene su
 * propia copia de `niceStep` y de las conversiones; NO se migra todavía — la
 * migración es deuda técnica anotada, no parte de esta fase.
 */

/**
 * Convertidores entre coordenadas matemáticas y píxeles.
 *
 * La vista se describe con `{ ox, oy, scaleX, scaleY }`: `(ox, oy)` es el origen
 * matemático en píxeles y las escalas son píxeles por unidad. El eje Y va al
 * revés que en pantalla, de ahí el signo.
 */
export function makeTransform({ ox, oy, scaleX, scaleY }) {
  return {
    toScreenX: (x) => ox + x * scaleX,
    toScreenY: (y) => oy - y * scaleY,
    toMathX: (sx) => (sx - ox) / scaleX,
    toMathY: (sy) => (oy - sy) / scaleY,
  };
}

/**
 * Paso de rejilla "redondo" (1, 2 ó 5 × 10ⁿ) que deja al menos `minPx` píxeles
 * entre líneas. Se calcula por eje: con escalas distintas en X e Y, un paso
 * único deja un eje apelmazado y el otro desierto.
 */
export function niceStep(scale, minPx = 70) {
  if (!isFinite(scale) || scale <= 0) return 1;
  const raw = minPx / scale;
  const mag = Math.pow(10, Math.floor(Math.log10(raw)));
  const norm = raw / mag;
  if (norm <= 1) return mag;
  if (norm <= 2) return 2 * mag;
  if (norm <= 5) return 5 * mag;
  return 10 * mag;
}

/**
 * Etiqueta de un tick con los decimales que pide su paso: con paso 0.5 sobra
 * "1.0" y con paso 0.05 falta.
 */
export function formatTick(value, step) {
  if (!isFinite(value)) return "";
  if (Math.abs(value) < step * 0.01) return "0";
  const decimals = Math.max(0, -Math.floor(Math.log10(step)));
  return value.toFixed(decimals);
}

/**
 * Vista ISOMÉTRICA: misma escala en X e Y, encuadrando el rectángulo pedido y
 * centrándolo en el lienzo.
 *
 * Es el requisito que separa la telaraña del gráfico de f(x). `FunctionGraph`
 * usa escalas independientes a propósito (arreglo de G1: sin eso no caben una
 * senoide y una parábola en la misma ventana). En un cobweb esa libertad es
 * veneno: si scaleX ≠ scaleY, la recta y = x deja de verse a 45° y el rebote
 * contra la diagonal —que es toda la intuición del método— se pierde.
 */
export function isoView({ width, height, xMin, xMax, yMin, yMax, padding = 0.08 }) {
  const spanX = Math.max(xMax - xMin, 1e-9);
  const spanY = Math.max(yMax - yMin, 1e-9);
  const usableW = width * (1 - 2 * padding);
  const usableH = height * (1 - 2 * padding);

  const scale = Math.max(Math.min(usableW / spanX, usableH / spanY), 1e-9);

  const cx = (xMin + xMax) / 2;
  const cy = (yMin + yMax) / 2;

  return {
    ox: width / 2 - cx * scale,
    oy: height / 2 + cy * scale,
    scaleX: scale,
    scaleY: scale,
  };
}

/** Recorre los múltiplos de `step` visibles en [min, max]. */
export function gridLines(min, max, step) {
  const out = [];
  if (!isFinite(min) || !isFinite(max) || !(step > 0)) return out;
  // Tope de seguridad: una vista degenerada no debe colgar el hilo de dibujo.
  const maxLines = 500;
  for (let v = Math.ceil(min / step) * step; v <= max && out.length < maxLines; v += step) {
    out.push(v);
  }
  return out;
}

// Colores por defecto (tema claro) por si se pide la paleta antes de que el
// elemento esté en el DOM y no haya estilos calculados que leer.
const FALLBACK = {
  bg: "#ffffff",
  text: "#6b6375",
  textStrong: "#08060d",
  border: "#e5e4e7",
  accent: "#aa3bff",
  accentSoft: "rgba(170, 59, 255, 0.1)",
  surface: "#f4f3ec",
};

/**
 * Paleta del gráfico leída de las variables CSS del tema (`index.css`), para
 * que el canvas siga a claro/oscuro en vez de llevar los colores cosidos.
 *
 * El canvas de `CalcularPage` tiene hoy el fondo `#1a1a2e` hardcodeado (pendiente
 * 5 de la hoja de ruta). La telaraña nace ya adaptable, y esta función queda
 * como la pieza que ese pendiente reutilizará en vez de resolverlo dos veces.
 */
export function getPlotPalette(element) {
  if (typeof window === "undefined" || !element) return { ...FALLBACK };

  const css = window.getComputedStyle(element);
  const read = (name, fallback) => {
    const value = css.getPropertyValue(name);
    return value && value.trim() ? value.trim() : fallback;
  };

  return {
    bg: read("--bg", FALLBACK.bg),
    text: read("--text", FALLBACK.text),
    textStrong: read("--text-h", FALLBACK.textStrong),
    border: read("--border", FALLBACK.border),
    accent: read("--accent", FALLBACK.accent),
    accentSoft: read("--accent-bg", FALLBACK.accentSoft),
    surface: read("--code-bg", FALLBACK.surface),
  };
}
