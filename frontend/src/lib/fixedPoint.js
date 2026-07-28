/**
 * Análisis de iteración de punto fijo, en el cliente.
 *
 * Sustituye lo que iba a pedirse al backend en FASE 2 (paso 2). Motivo: los
 * `gx_candidates` de `auto_params.py` resultaron tener SIEMPRE un solo elemento
 * —`x − f(x)/f'(x)`, con |g'| = 0 en la raíz— así que jamás dan el contraste
 * "una g converge y otra escapa", que es la lección de la telaraña. Ver §5/§7.
 *
 * Aquí nada se afirma de antemano: |g'| se MIDE por diferencias finitas sobre la
 * g(x) que haya en pantalla, sea un preset o algo que el alumno acabe de teclear.
 *
 * Y la iteración se hace aquí, no en `/method/punto_fijo`, porque ese endpoint se
 * niega a iterar cuando |g'(x₀)| ≥ 1 (`_check_applicability`): correcto para una
 * calculadora, inservible para enseñar, ya que la trayectoria divergente es
 * justo la que hay que ver dibujada.
 */

// Con extensión explícita: Vite la resuelve igual, y así estos módulos se
// pueden probar con `node` a secas, sin montar un runner de tests.
import { compileExpr } from "./evalExpr.js";

/** |x| a partir del cual damos la órbita por escapada. */
const ESCAPE = 1e8;

/**
 * Derivada numérica por diferencia central.
 *
 * El paso se escala con |x|: un h fijo es demasiado grande cerca de 0 y
 * demasiado pequeño (lo devora el redondeo) en x ~ 10⁶.
 */
export function derivativeAt(fn, x, h = 1e-6 * Math.max(1, Math.abs(x))) {
  if (typeof fn !== "function" || !isFinite(x)) return NaN;
  const a = fn(x + h);
  const b = fn(x - h);
  if (!isFinite(a) || !isFinite(b)) return NaN;
  return (a - b) / (2 * h);
}

/**
 * Mide g'(x) y dice si el punto fijo es atractor.
 *
 * `converges` sólo es fiable EN la raíz: el criterio |g'(r)| < 1 es local. En
 * otro punto es una pista, no una garantía — de ahí que se devuelva también el
 * punto en el que se midió, para que la UI no prometa de más.
 */
export function analyzeG(gSource, x) {
  const g = compileExpr(gSource);
  if (!g) return { ok: false, reason: "no-compila", at: x, gp: NaN, absGp: NaN, converges: false };

  const gx = g(x);
  if (!isFinite(gx)) {
    return { ok: false, reason: "fuera-de-dominio", at: x, gp: NaN, absGp: NaN, converges: false };
  }

  const gp = derivativeAt(g, x);
  if (!isFinite(gp)) {
    return { ok: false, reason: "derivada-indefinida", at: x, gp: NaN, absGp: NaN, converges: false };
  }

  return { ok: true, reason: null, at: x, gp, absGp: Math.abs(gp), converges: Math.abs(gp) < 1 };
}

/**
 * Itera xₙ₊₁ = g(xₙ) y devuelve la órbita completa, converja o no.
 *
 * `status`:
 *   "convergió"  — dos iterados consecutivos dentro de `tol`
 *   "escapó"     — la órbita se fue a infinito o salió del dominio
 *   "sin-cerrar" — agotó `maxIter` sin ninguna de las dos cosas (órbita lenta o cíclica)
 *   "no-compila" — g(x) no se pudo interpretar
 *
 * Los valores por defecto son de DIBUJO, no de cálculo: `tol` es absoluta y muy
 * por debajo de un píxel en cualquier encuadre razonable, y `maxIter` da margen
 * a la convergencia lineal — con |g'| ≈ 0.67 hacen falta unas 40 iteraciones
 * para ganar 7 cifras, y cortar antes etiquetaría como "sin cerrar" una órbita
 * que a ojo lleva rato pegada al punto fijo. Para un resultado numérico de
 * verdad está la calculadora, que usa la tolerancia del backend (Excel).
 */
export function iterateG(gSource, x0, { maxIter = 60, tol = 1e-7 } = {}) {
  const g = compileExpr(gSource);
  if (!g) return { status: "no-compila", points: [], root: null };

  const points = [];
  let x = Number(x0);
  if (!isFinite(x)) return { status: "escapó", points, root: null };

  for (let k = 0; k < maxIter; k++) {
    const gx = g(x);

    if (!isFinite(gx) || Math.abs(gx) > ESCAPE) {
      points.push({ k, x, gx });
      return { status: "escapó", points, root: null };
    }

    points.push({ k, x, gx });

    if (Math.abs(gx - x) < tol) {
      return { status: "convergió", points, root: gx };
    }
    x = gx;
  }

  return { status: "sin-cerrar", points, root: null };
}

/**
 * Convierte la órbita en los segmentos de la telaraña.
 *
 * El cobweb se dibuja alternando: desde (x, x) subir vertical hasta (x, g(x)),
 * y de ahí ir horizontal hasta la diagonal, en (g(x), g(x)). Repetir. Ese
 * zigzag entre curva y diagonal es lo que hace visible la convergencia.
 *
 * El primer segmento arranca en el eje X, en (x₀, 0), para que se vea de dónde
 * sale la órbita; los demás nacen ya sobre la diagonal.
 */
export function cobwebPath(points) {
  const segments = [];
  if (!Array.isArray(points) || points.length === 0) return segments;

  const first = points[0];
  segments.push({ tipo: "vertical", x1: first.x, y1: 0, x2: first.x, y2: first.gx });

  for (let i = 0; i < points.length; i++) {
    const { x, gx } = points[i];
    if (i > 0) segments.push({ tipo: "vertical", x1: x, y1: x, x2: x, y2: gx });
    segments.push({ tipo: "horizontal", x1: x, y1: gx, x2: gx, y2: gx });
  }

  return segments;
}
