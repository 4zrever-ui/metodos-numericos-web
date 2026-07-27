/**
 * Evaluación de expresiones matemáticas en el cliente.
 *
 * Nace en FASE 2 para la telaraña de punto fijo: iterar g(x) 30 veces y muestrear
 * la curva miles de veces tiene que ser barato y no depender del backend
 * (`punto_fijo.py` se niega a iterar cuando |g'(x₀)| ≥ 1, y esa es justo la mitad
 * de la lección — ver CLAUDE.md §5, FASE 2).
 *
 * Es hermano del `evalF` privado de `CalcularPage`, NO su reemplazo todavía:
 * la migración de la calculadora a este módulo está anotada como deuda técnica
 * (decisión del director: no mezclar ese riesgo con una feature nueva).
 *
 * Dos diferencias deliberadas respecto de aquel `evalF`:
 *
 * 1. Traduce en UNA sola pasada con tabla de nombres. Encadenar `.replace()`
 *    por función es una trampa: en cuanto dos nombres comparten destino
 *    (`Abs` y `abs` → `Math.abs`) el segundo reemplazo vuelve a morder el
 *    resultado del primero y produce `Math.Math.abs`.
 * 2. Entiende lo que imprime SymPy (`Abs`, `sqrt`, `exp`, `log`, `E`) y también
 *    `cbrt`, porque el `gx` de `/params` llega como `str(sympy_expr)` y el
 *    normalizador de entrada convierte `\sqrt[3]{}` en `cbrt()`.
 *
 * Devuelve `null` al COMPILAR cuando la expresión no se entiende, y `NaN` al
 * EVALUAR un punto donde no está definida. La telaraña necesita distinguirlas:
 * "no supe leer tu g(x)" y "g(x) se escapó" son mensajes distintos.
 */

// Nombres reconocidos → su equivalente en JS. Todo lo que no esté aquí se
// considera desconocido y hace fallar la compilación (ver paso 4 de `toJs`).
const NAMES = {
  // Trigonométricas
  sin: "Math.sin",   cos: "Math.cos",   tan: "Math.tan",
  asin: "Math.asin", acos: "Math.acos", atan: "Math.atan",
  sinh: "Math.sinh", cosh: "Math.cosh", tanh: "Math.tanh",
  // Exponencial y logaritmos (log = natural, como SymPy y como el backend)
  exp: "Math.exp", log: "Math.log", ln: "Math.log", log10: "Math.log10",
  // Raíces y valor absoluto — `Abs` con mayúscula es como lo imprime SymPy
  sqrt: "Math.sqrt", cbrt: "Math.cbrt", abs: "Math.abs", Abs: "Math.abs",
  sign: "Math.sign",
  // Constantes
  pi: "Math.PI", PI: "Math.PI", E: "Math.E", e: "Math.E",
  // La variable se traduce a sí misma
  x: "x",
};

/** Traduce la expresión a JS. Devuelve null si contiene algo no reconocido. */
function toJs(source) {
  if (typeof source !== "string") return null;
  const trimmed = source.trim();
  if (!trimmed) return null;

  // 1. Potencias: `^` es XOR en JS, aquí siempre significa exponente.
  let expr = trimmed.replace(/\^/g, "**");

  // 2. Multiplicación implícita, sólo en los casos sin ambigüedad:
  //    `2(x+1)` y `(x+1)(x-1)`. NO tras letra: rompía `sin(x)` → `Math.sin*(x)`
  //    (el bug del commit b3b085a, que dejaba en blanco toda curva con paréntesis).
  expr = expr.replace(/([0-9)])(\s*)\(/g, "$1*(");

  //    `2x` y `3pi`: dígito pegado a nombre. La excepción es la `e` de un
  //    exponente: en `1e-5` esa letra es parte del número, y meterle un `*` lo
  //    convertiría en `1*e-5` (≈ −2.28 en lugar de 0.00001).
  expr = expr.replace(
    /([0-9])(\s*)([A-Za-z_])/g,
    (match, digit, space, letter, offset, whole) => {
      if (letter === "e" || letter === "E") {
        const rest = whole.slice(offset + match.length);
        if (/^[+-]?[0-9]/.test(rest)) return match;   // es un exponente: no tocar
      }
      return digit + "*" + letter;
    }
  );

  // 3. Nombres, en una sola pasada. El `\b` inicial evita morder la `e` de un
  //    `1e-5` y, en general, las letras que van dentro de un número.
  expr = expr.replace(/\b[A-Za-z_][A-Za-z_0-9]*/g, (name) =>
    Object.prototype.hasOwnProperty.call(NAMES, name) ? NAMES[name] : name
  );

  // 4. Si sobra algún identificador que no sea `x` ni un `Math.algo`, la
  //    expresión menciona algo que no sabemos evaluar: mejor decirlo que
  //    devolver NaN en silencio y dibujar un lienzo en blanco.
  const leftovers = expr
    .replace(/Math\.[A-Za-z0-9_]+/g, "")
    .match(/\b[A-Za-z_][A-Za-z_0-9]*/g);
  if (leftovers && leftovers.some((name) => name !== "x")) return null;

  return expr;
}

// Compilar con `new Function` no es gratis; la telaraña reevalúa la misma g(x)
// miles de veces por dibujo.
const cache = new Map();
const CACHE_LIMIT = 64;

/**
 * Compila una expresión en una función `(x) => number`.
 * Devuelve `null` si la expresión no se puede interpretar.
 */
export function compileExpr(source) {
  const key = typeof source === "string" ? source.trim() : "";
  if (cache.has(key)) return cache.get(key);

  const js = toJs(source);
  let fn = null;
  if (js !== null) {
    try {
      const raw = new Function("x", `"use strict"; return (${js});`);
      // Prueba de humo: si ni siquiera evalúa en un punto corriente sin lanzar,
      // no es utilizable. (Un NaN legítimo —dominio— sí se acepta.)
      raw(1);
      fn = (x) => {
        try {
          const y = raw(x);
          return typeof y === "number" ? y : NaN;
        } catch {
          return NaN;
        }
      };
    } catch {
      fn = null;
    }
  }

  if (cache.size >= CACHE_LIMIT) cache.clear();
  cache.set(key, fn);
  return fn;
}

/**
 * Evalúa una expresión en un punto. Atajo para usos sueltos; si vas a evaluar
 * muchas veces la misma expresión, usa `compileExpr` y guarda la función.
 */
export function evalExpr(source, x) {
  const fn = compileExpr(source);
  return fn ? fn(x) : NaN;
}

/** ¿Se entiende esta expresión? Útil para avisar antes de dibujar nada. */
export function isValidExpr(source) {
  return compileExpr(source) !== null;
}
