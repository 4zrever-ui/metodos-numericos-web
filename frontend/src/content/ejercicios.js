/**
 * Ejercicios de la pestaña Practicar.
 *
 * Conjunto FIJO y curado a mano (decisión D1). El banco que rota por fecha que
 * describe `VISION_PLATAFORMA.md` §3 es pieza de fase posterior: la parte difícil
 * de FASE 3 es el constructor de fórmulas, y generar contenido en la misma fase
 * habría metido dos riesgos en el mismo movimiento.
 *
 * Mismo patrón que `content/gxPresets.js`: aquí sólo se describe el ejercicio.
 * **Las fórmulas correctas NO están aquí** — las sirve el backend desde
 * `formula_specs.py`, fijado contra las plantillas de Excel por
 * `test_formula_specs.py`. Si estuvieran duplicadas en el frontend habría dos
 * fuentes de verdad y acabarían divergiendo, que es justo lo que ese test evita.
 *
 * Métodos cubiertos: Newton y Bisección (decisión D5), uno de derivada y uno de
 * intervalo, antes de extender a los catorce.
 */

export const EJERCICIOS = [
  {
    id: "cubica-newton",
    equation: "x**3 - 2*x - 5",
    etiqueta: "x³ − 2x − 5 = 0",
    metodo: "newton",
    metodoLabel: "Newton-Raphson",
    enunciado:
      "El caso clásico. Construye la fila de iteración: cada columna se apoya en " +
      "las de su izquierda, y la de xₖ₊₁ es el paso de Newton propiamente dicho.",
  },
  {
    id: "cubica-biseccion",
    equation: "x**3 - 2*x - 5",
    etiqueta: "x³ − 2x − 5 = 0",
    metodo: "biseccion",
    metodoLabel: "Bisección",
    enunciado:
      "La misma ecuación, con un método de intervalo. Fíjate en las columnas a y b: " +
      "no se calculan, se DECIDEN según el signo de f(a)·f(c) de la fila anterior.",
  },
  {
    id: "coseno-newton",
    equation: "cos(x) - x",
    etiqueta: "cos(x) − x = 0",
    metodo: "newton",
    metodoLabel: "Newton-Raphson",
    enunciado:
      "Con una función trascendente la fórmula de la columna f(xₖ) deja de ser un " +
      "polinomio, pero la estructura de la fila es exactamente la misma.",
  },
  {
    id: "cubica3-biseccion",
    equation: "x**3 - 4*x + 1",
    etiqueta: "x³ − 4x + 1 = 0",
    metodo: "biseccion",
    metodoLabel: "Bisección",
    enunciado:
      "Esta cúbica tiene tres raíces reales. El intervalo de partida decide a cuál " +
      "converge: la bisección encuentra la que tenga encerrada, no la más cercana a cero.",
  },
];

/** Busca un ejercicio por su id. */
export function ejercicioPorId(id) {
  return EJERCICIOS.find((e) => e.id === id) ?? null;
}
