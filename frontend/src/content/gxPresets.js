/**
 * Ecuaciones de ejemplo con varios reordenamientos g(x), para la telaraña.
 *
 * Existe porque el backend no puede darlas: `auto_params` genera una sola g,
 * `x − f(x)/f'(x)`, que converge siempre (|g'| = 0 en la raíz) y produce el
 * cobweb menos ilustrativo posible. La gracia de punto fijo es justo que la
 * MISMA ecuación admite varias g y no todas sirven — eso hay que curarlo a mano.
 *
 * IMPORTANTE: aquí no se afirma cuál converge. Las `nota` describen el ÁLGEBRA
 * del reordenamiento, no su resultado; el veredicto lo mide `analyzeG` sobre la
 * g real en el punto real. Así la página no puede mentir aunque me equivoque yo.
 *
 * `expr` va en la notación que entiende `evalExpr` (la misma que el backend).
 */

export const GX_PRESETS = [
  {
    equation: "x**3 - 2*x - 5",
    etiqueta: "x³ − 2x − 5 = 0",
    latex: String.raw`x^3 - 2x - 5 = 0`,
    x0: 2,
    raiz: 2.0945514815,
    nota:
      "El ejemplo canónico de los libros: tres formas de despejar la misma " +
      "ecuación, y no las tres sirven.",
    gxs: [
      {
        expr: "cbrt(2*x + 5)",
        latex: String.raw`g(x) = \sqrt[3]{2x + 5}`,
        nota: "Despeja el x³ y saca la raíz cúbica.",
      },
      {
        expr: "(x**3 - 5)/2",
        latex: String.raw`g(x) = \frac{x^3 - 5}{2}`,
        nota: "Despeja el término lineal −2x.",
      },
      {
        expr: "5/(x**2 - 2)",
        latex: String.raw`g(x) = \frac{5}{x^2 - 2}`,
        nota: "Factoriza x·(x² − 2) = 5 y despeja la x de fuera.",
      },
    ],
  },
  {
    equation: "cos(x) - x",
    etiqueta: "cos(x) − x = 0",
    latex: String.raw`\cos x - x = 0`,
    x0: 1,
    raiz: 0.7390851332,
    nota:
      "Con g'(r) negativa la órbita no sube en escalera: rodea al punto fijo " +
      "en espiral, saltando de un lado a otro.",
    gxs: [
      {
        expr: "cos(x)",
        latex: String.raw`g(x) = \cos x`,
        nota: "La ecuación ya viene despejada: x = cos x.",
      },
    ],
  },
  {
    equation: "exp(-x) - x",
    etiqueta: "e^(−x) − x = 0",
    latex: String.raw`e^{-x} - x = 0`,
    x0: 0.5,
    raiz: 0.5671432904,
    nota: "Otra espiral, y un buen contraste con la escalera de la cúbica.",
    gxs: [
      {
        expr: "exp(-x)",
        latex: String.raw`g(x) = e^{-x}`,
        nota: "Despejada de entrada: x = e^(−x).",
      },
    ],
  },
  {
    equation: "x**2 - 3*x + 2",
    etiqueta: "x² − 3x + 2 = 0",
    latex: String.raw`x^2 - 3x + 2 = 0`,
    x0: 0.5,
    raiz: 1,
    nota:
      "Dos raíces (1 y 2) y UNA sola g(x). El mismo reordenamiento atrae a una " +
      "y repele a la otra: la convergencia no es propiedad de g, sino de g en " +
      "cada raíz.",
    gxs: [
      {
        expr: "(x**2 + 2)/3",
        latex: String.raw`g(x) = \frac{x^2 + 2}{3}`,
        nota: "Despeja el término −3x. Pruébalo con x₀ = 0.5 y luego con x₀ = 2.5.",
      },
    ],
  },
];

/** Busca los presets de una ecuación concreta (o `null` si no es de ejemplo). */
export function presetsFor(equation) {
  const key = (equation || "").replace(/\s+/g, "");
  return GX_PRESETS.find((p) => p.equation.replace(/\s+/g, "") === key) || null;
}
