/**
 * Resolución de una hoja de cálculo simulada.
 *
 * El backend (`/practicar/plantilla`) manda la hoja fila a fila con el tipo de
 * cada celda. Aquí se calculan sus valores, que hacen falta para dos cosas:
 * enseñar la tabla resuelta y, sobre todo, **corregir por valor** la fórmula que
 * escriba el alumno (decisión D3) — sin valores no hay con qué comparar.
 *
 * Por qué se resuelve por pasadas y no en un orden fijo
 * -----------------------------------------------------
 * Las celdas no se pueden evaluar de izquierda a derecha sin más: en Bisección,
 * `C` (el punto medio) depende de `D` (el extremo derecho), que va DESPUÉS en el
 * alfabeto. Ordenar las dependencias a mano por método es justo la clase de
 * detalle que se rompe al añadir el tercero. Se repiten pasadas hasta que
 * ningún valor cambia, que da igual el orden y además detecta referencias
 * circulares (se agotan las pasadas y `estable` sale `false`).
 */

import { compararFormulas, evaluarFormula, referenciasDe } from "./celdas.js";

/** Convierte el contenido literal de una celda en número cuando lo es. */
function comoValor(texto) {
  if (texto === "" || texto === null || texto === undefined) return "";
  const n = Number(texto);
  return Number.isFinite(n) ? n : texto;
}

/**
 * Calcula el valor de cada celda de la hoja.
 *
 * Devuelve `{ valores, pasadas, estable, errores }`.
 * `valores` es un mapa `{ B3: 2.1, ... }` listo para pasárselo a `celdas.js`.
 */
export function resolverHoja(hoja, { maxPasadas = 12 } = {}) {
  const valores = {};
  const errores = {};
  if (!hoja?.filas) return { valores, pasadas: 0, estable: true, errores };

  const celdas = hoja.filas.flatMap((f) => f.celdas);

  // Primero lo que no depende de nadie.
  for (const c of celdas) {
    if (c.tipo === "indice" || c.tipo === "inicial") valores[c.ref] = comoValor(c.contenido);
    else if (c.tipo === "vacia") valores[c.ref] = "";
  }

  for (let pasada = 1; pasada <= maxPasadas; pasada++) {
    let cambios = 0;
    for (const c of celdas) {
      if (c.tipo !== "formula") continue;
      const r = evaluarFormula(c.contenido, valores);
      const nuevo = r.ok ? r.valor : null;
      if (!r.ok) errores[c.ref] = r.error; else delete errores[c.ref];
      if (!Object.is(valores[c.ref], nuevo)) {
        valores[c.ref] = nuevo;
        cambios++;
      }
    }
    if (cambios === 0) return { valores, pasadas: pasada, estable: true, errores };
  }

  return { valores, pasadas: maxPasadas, estable: false, errores };
}

/** La fórmula correcta de una celda, tal como la manda el backend. */
export function formulaCanonica(hoja, ref) {
  for (const fila of hoja?.filas ?? []) {
    for (const c of fila.celdas) if (c.ref === ref) return c.contenido;
  }
  return null;
}

/** Las celdas que el alumno debe escribir: las de tipo fórmula de una fila. */
export function celdasAEscribir(hoja, k) {
  const fila = (hoja?.filas ?? []).find((f) => f.k === k);
  return (fila?.celdas ?? []).filter((c) => c.tipo === "formula");
}

// Factores con los que se sacuden los valores de las celdas referenciadas.
// Cubren órdenes de magnitud muy distintos a propósito: el primer caso que
// obligó a esto fue una tolerancia mal escrita, y para pillarla hace falta un
// valor que caiga ENTRE los dos umbrales.
const FACTORES = [0.5, 2, 1e-3, 1e-6, 1e3, -1, 0.05, -0.3, 7];

// Un escenario por factor: así, con una fórmula que referencia UNA sola celda,
// se recorren todos. (Un reparto con paso 3 los saltaba y dejaba escapar de
// nuevo el caso del umbral, que necesita un factor pequeño concreto.)
const N_ESCENARIOS = FACTORES.length;

/**
 * Corrige la fórmula que ha escrito el alumno.
 *
 * Compara POR VALOR (D3), pero **no en un solo punto**. Medido al verificar el
 * paso 5: `IF(I3<0.00001,"SI","NO")` y `IF(I3<0.1,"SI","NO")` devuelven las dos
 * `"NO"` con los datos reales de esa fila, así que una tolerancia mal escrita
 * pasaba por correcta. Comparar en un único escenario no distingue una fórmula
 * equivalente de una que **acierta por casualidad**.
 *
 * Por eso se evalúan las dos fórmulas también con los valores sacudidos: si en
 * algún escenario discrepan, no son equivalentes. Sigue siendo corrección por
 * valor —dos formas distintas de escribir lo mismo siguen valiendo—, sólo que
 * con más de un dato.
 *
 * **Cada celda se sacude por SEPARADO, y esto es lo que hace que funcione.**
 * La primera versión multiplicaba todas las celdas por el mismo factor, y dejó
 * pasar el criterio del intervalo de Bisección escrito al revés
 * (`IF(E2*F2<0,B2,D2)` en lugar de `...,B2,C2)`): con los datos reales
 * `E2*F2 < 0` es cierto, así que sólo se toma la rama verdadera y la falsa
 * nunca llega a compararse — y escalar E2 y F2 a la vez no cambia el signo del
 * producto, ni siquiera con −1, porque (−E)(−F) sigue siendo negativo. Con
 * factores distintos por celda el producto sí cambia de signo, la condición se
 * invierte y la rama falsa queda expuesta.
 */
export function validarCelda(hoja, ref, escrita, valores) {
  const canonica = formulaCanonica(hoja, ref);
  if (!canonica) return { veredicto: "sin-canonica", canonica: null };

  const base = compararFormulas(escrita, canonica, valores);
  if (base.veredicto !== "correcta") return { ...base, canonica };

  const refs = [...new Set(referenciasDe(canonica))];
  const numericas = refs.filter((r) => typeof valores[r] === "number" && Number.isFinite(valores[r]));
  if (numericas.length === 0) return { veredicto: "correcta", canonica };

  for (let escenario = 0; escenario < N_ESCENARIOS; escenario++) {
    const sacudidos = { ...valores };
    numericas.forEach((r, j) => {
      // Reparto determinista: cada celda recibe un factor distinto, y el reparto
      // cambia con el escenario. Sin aleatoriedad, para que un fallo se pueda
      // reproducir tal cual.
      const factor = FACTORES[(escenario + j * 4) % FACTORES.length];
      sacudidos[r] = valores[r] * factor;
    });

    const cmp = compararFormulas(escrita, canonica, sacudidos);
    // Si la canónica no evalúa con esos valores, el escenario no dice nada.
    if (cmp.veredicto === "canonica-invalida" || cmp.veredicto === "no-evalua") continue;
    if (cmp.veredicto !== "correcta") {
      return {
        veredicto: "coincide-por-casualidad",
        canonica,
        obtenido: cmp.obtenido,
        esperado: cmp.esperado,
        escenario,
      };
    }
  }

  return { veredicto: "correcta", canonica };
}
