/**
 * Motor de celdas: evalúa fórmulas de hoja de cálculo en el cliente.
 *
 * Es la pieza que permite corregir a un alumno por VALOR y no por cadena
 * (decisión D3 de FASE 3): dos fórmulas escritas distinto pero equivalentes
 * —`B3-(C3/D3)` y `B3-C3/D3`— deben darse las dos por buenas.
 *
 * Nace de cero porque el proyecto NO tenía evaluador de fórmulas de Excel en
 * ningún lenguaje: `formulas` figura en la lista de dependencias de CLAUDE.md
 * §8, pero ningún archivo la importa (verificado en todo el repo).
 *
 * NO reutiliza `evalExpr` tal cual, y la razón es concreta: aquel evaluador
 * exige que el único identificador sea `x`, así que rechaza `B3` y `C3` de
 * plano; y no sabe de `IF`, ni de cadenas, ni de comparaciones, que es
 * justamente lo que distingue una hoja de cálculo de una expresión. Comparte
 * en cambio su enfoque: traducir a JS en pasadas controladas y ejecutar con
 * una lista blanca de nombres.
 *
 * Cubre lo que usan las plantillas de Newton y Bisección (decisión D5):
 * aritmética, `^`, comparaciones, cadenas, ABS e IF.
 */

// Funciones de hoja disponibles dentro de la fórmula. Se inyectan como
// argumentos de la función compilada, así que no dependen del ámbito global.
const FUNCIONES = {
  ABS: Math.abs,
  SQRT: Math.sqrt,
  EXP: Math.exp,
  LN: Math.log,
  SIN: Math.sin,
  COS: Math.cos,
  TAN: Math.tan,
  SIGN: Math.sign,
  POWER: (a, b) => a ** b,
  ROUND: (v, d = 0) => { const f = 10 ** d; return Math.round(v * f) / f; },
  MIN: Math.min,
  MAX: Math.max,
  IF: (cond, siVerdad, siFalso) => (cond ? siVerdad : siFalso),
  AND: (...a) => a.every(Boolean),
  OR: (...a) => a.some(Boolean),
  NOT: (v) => !v,
};

const NOMBRES_FUNCION = Object.keys(FUNCIONES);
const PERMITIDOS = new Set([...NOMBRES_FUNCION, "NaN", "true", "false"]);

/** Referencia de celda tipo B3, AA12. */
const REFERENCIA = /\b([A-Z]{1,2})([0-9]{1,4})\b/g;

/** Cadenas entre comillas dobles: hay que respetarlas al traducir. */
const CADENA = /"[^"]*"/g;

/**
 * Traduce una fórmula de hoja a JavaScript.
 * Devuelve `{ js, refs, desconocida }`; `js` es null si algo no se entiende.
 */
function aJs(formula, valores) {
  if (typeof formula !== "string") return null;
  let s = formula.trim();
  if (!s) return null;
  if (s.startsWith("=")) s = s.slice(1);

  // Las cadenas se apartan para que ni las referencias ni los operadores las
  // toquen: dentro de "SI" no hay nada que traducir. El marcador lleva letras
  // a propósito — uno numérico se confundiría al restaurarlo con los números
  // de la propia fórmula, como el 0.00001 del criterio de convergencia.
  const cadenas = [];
  const guardar = (lit) => {
    cadenas.push(lit);
    return `__S${cadenas.length - 1}__`;
  };
  s = s.replace(CADENA, guardar);

  const refs = [];
  let desconocida = null;

  // Referencias → su valor. Una celda vacía vale 0, como en Excel.
  s = s.replace(REFERENCIA, (ref) => {
    if (PERMITIDOS.has(ref)) return ref;
    refs.push(ref);
    const v = valores?.[ref];
    if (v === undefined || v === null || v === "") return "0";
    if (typeof v === "number") return Number.isFinite(v) ? `(${v})` : "NaN";
    if (typeof v === "string") return guardar(`"${v.replace(/"/g, '\\"')}"`);
    if (typeof v === "boolean") return String(v);
    return "0";
  });

  // Operadores, en UNA sola pasada. Encadenar reemplazos rompía el `!==` recién
  // creado: el reemplazo posterior de `=` lo convertía en `!======`.
  s = s.replace(/<=|>=|<>|=/g, (op) => {
    if (op === "<=") return "<=";
    if (op === ">=") return ">=";
    if (op === "<>") return "!==";
    return "===";
  });

  s = s.replace(/\^/g, "**");

  // Nombres: sólo funciones conocidas y los marcadores de cadena. Cualquier
  // otro identificador (una función que no cubrimos, una referencia mal
  // escrita como "B" sola) invalida la fórmula en vez de dar NaN en silencio.
  s.replace(/\b[A-Za-z_][A-Za-z_0-9]*/g, (nombre) => {
    if (!PERMITIDOS.has(nombre) && !/^__S\d+__$/.test(nombre)) desconocida = nombre;
    return nombre;
  });
  if (desconocida) return { js: null, refs, desconocida };

  s = s.replace(/__S(\d+)__/g, (_, i) => cadenas[Number(i)]);

  return { js: s, refs, desconocida: null };
}

/**
 * Evalúa una fórmula con los valores de las celdas de las que depende.
 *
 * `error` distingue los casos que el alumno necesita ver distintos:
 *   "no-entiendo"      no se pudo interpretar
 *   "nombre:XYZ"       usa algo que no reconocemos
 *   "division-por-cero" / "indefinido"
 */
export function evaluarFormula(formula, valores = {}) {
  const t = aJs(formula, valores);
  if (!t) return { ok: false, valor: null, tipo: null, error: "no-entiendo", refs: [] };
  if (t.desconocida) {
    return { ok: false, valor: null, tipo: null, error: `nombre:${t.desconocida}`, refs: t.refs };
  }

  try {
    const fn = new Function(...NOMBRES_FUNCION, `"use strict"; return (${t.js});`);
    const valor = fn(...NOMBRES_FUNCION.map((n) => FUNCIONES[n]));
    const tipo =
      typeof valor === "number" ? "numero"
      : typeof valor === "string" ? "texto"
      : typeof valor === "boolean" ? "logico"
      : "otro";

    if (tipo === "numero" && !Number.isFinite(valor)) {
      return {
        ok: false, valor, tipo,
        error: Number.isNaN(valor) ? "indefinido" : "division-por-cero",
        refs: t.refs,
      };
    }
    return { ok: true, valor, tipo, error: null, refs: t.refs };
  } catch {
    return { ok: false, valor: null, tipo: null, error: "no-entiendo", refs: t.refs };
  }
}

/** Las celdas de las que depende una fórmula, sin evaluarla. */
export function referenciasDe(formula) {
  const t = aJs(formula, {});
  return t ? t.refs : [];
}

/**
 * ¿La fórmula del alumno hace lo mismo que la correcta?
 *
 * Se comparan por VALOR (D3), no por cadena: se evalúan las dos con los mismos
 * datos y se mira el resultado. Así `B3-(C3/D3)` y `B3-C3/D3` valen igual, que
 * es lo justo — el alumno está aprendiendo el método, no una ortografía.
 *
 * La tolerancia es relativa porque los valores de estas tablas van de 1e-9 a
 * 1e3 según la columna y la iteración; una absoluta daría por buena cualquier
 * cosa en las columnas de error.
 */
export function compararFormulas(escrita, canonica, valores = {}, tol = 1e-9) {
  const b = evaluarFormula(canonica, valores);
  if (!b.ok) return { veredicto: "canonica-invalida", detalle: b.error };

  const a = evaluarFormula(escrita, valores);
  if (!a.ok) return { veredicto: "no-evalua", detalle: a.error, esperado: b.valor };

  if (a.tipo !== b.tipo) {
    return { veredicto: "tipo-distinto", obtenido: a.valor, esperado: b.valor };
  }

  if (a.tipo === "numero") {
    const escala = Math.max(Math.abs(b.valor), 1);
    const iguales = Math.abs(a.valor - b.valor) <= tol * escala;
    return { veredicto: iguales ? "correcta" : "valor-distinto", obtenido: a.valor, esperado: b.valor };
  }

  return {
    veredicto: a.valor === b.valor ? "correcta" : "valor-distinto",
    obtenido: a.valor, esperado: b.valor,
  };
}
