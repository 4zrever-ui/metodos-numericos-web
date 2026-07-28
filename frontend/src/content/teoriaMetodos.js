/**
 * Catálogo de teoría de los 14 métodos.
 *
 * Vive en el frontend y no en el backend por una razón concreta: el backend sólo
 * produce LaTeX **por ecuación** (`f_latex`, `fp_latex`, `fpp_latex`, `gx_latex`),
 * nunca **por método** — su `formula_description` es texto Unicode plano
 * (`"xₙ₊₁ = xₙ − f(xₙ) / f'(xₙ)"`), no LaTeX. La teoría es contenido redactado,
 * no dato calculado.
 *
 * Las `recurrencia` reproducen **exactamente** la fórmula que implementa cada
 * `backend/methods/*.py`, no la de un libro: si el código y el libro discrepan,
 * manda el código y la discrepancia se anota en `advertencia`. Un alumno que
 * compare la teoría con la tabla de iteraciones tiene que ver lo mismo.
 *
 * Esquema de cada ficha:
 *   label        nombre visible (igual que en la calculadora)
 *   familia      agrupación de CLAUDE.md §3
 *   idea         2-3 frases en lenguaje llano: qué hace y por qué funciona
 *   recurrencia  LaTeX de la fórmula de iteración
 *   condicion    LaTeX de la condición que debe cumplirse (o null)
 *   cuandoAplica cuándo elegirlo, en prosa
 *   orden        { valor, etiqueta, nota } — orden de convergencia
 *   ventajas / desventajas
 *   advertencia  desviación conocida de ESTE proyecto (o null) — ver §4/§7
 *   demo         "cobweb" si tiene demostración interactiva, si no null
 */

export const TEORIA = {
  // ── Métodos de intervalo ───────────────────────────────────────────────────
  biseccion: {
    label: "Bisección",
    familia: "intervalo",
    idea:
      "Si f cambia de signo entre a y b, y es continua, en algún punto de en medio vale cero. " +
      "Se parte el intervalo por la mitad y se conserva la mitad donde el signo sigue cambiando. " +
      "Repitiendo, el intervalo se encoge hasta atrapar la raíz.",
    recurrencia: String.raw`c_n = \frac{a_n + b_n}{2}`,
    condicion: String.raw`f(a)\cdot f(b) < 0`,
    cuandoAplica:
      "Cuando quieres una garantía y no tienes prisa. Es el único de los 14 que no puede " +
      "fallar si arrancas bien: el teorema del valor intermedio hace el trabajo.",
    orden: {
      valor: 1,
      etiqueta: "Lineal",
      nota: "El error se divide por 2 en cada paso, siempre. Ni más rápido ni más lento según la función.",
    },
    ventajas: [
      "Convergencia garantizada si hay cambio de signo.",
      "No necesita derivadas.",
      "Se sabe de antemano cuántas iteraciones harán falta.",
    ],
    desventajas: [
      "Lento comparado con todo lo demás.",
      "Necesita un intervalo que encierre la raíz.",
      "No ve raíces donde f toca el eje sin cruzarlo (multiplicidad par).",
    ],
    advertencia: null,
    demo: null,
  },

  regula_falsi: {
    label: "Regula Falsi",
    familia: "intervalo",
    idea:
      "La misma idea de la bisección, pero en vez de partir por la mitad a ciegas, se traza la " +
      "recta que une (a, f(a)) con (b, f(b)) y se corta donde esa recta cruza el eje. " +
      "Aprovecha la magnitud de f, no sólo su signo.",
    recurrencia: String.raw`c = a - \frac{f(a)\,(b - a)}{f(b) - f(a)}`,
    condicion: String.raw`f(a)\cdot f(b) < 0`,
    cuandoAplica:
      "Cuando tienes un intervalo válido y quieres ir más rápido que la bisección sin perder " +
      "la garantía de que la raíz sigue encerrada.",
    orden: {
      valor: 1,
      etiqueta: "Lineal",
      nota:
        "Suele batir a la bisección en la práctica, pero si la función es muy curva un extremo " +
        "se queda clavado y el intervalo deja de encogerse por ese lado.",
    },
    ventajas: [
      "Mantiene la raíz encerrada en todo momento.",
      "No necesita derivadas.",
      "Normalmente más rápido que la bisección.",
    ],
    desventajas: [
      "Un extremo puede quedarse fijo y frenar la convergencia.",
      "Necesita un intervalo que encierre la raíz.",
    ],
    advertencia: null,
    demo: null,
  },

  // ── Punto fijo y aceleración ───────────────────────────────────────────────
  punto_fijo: {
    label: "Punto Fijo",
    familia: "punto-fijo",
    idea:
      "Se reescribe f(x) = 0 como x = g(x). Entonces la raíz es un punto que g deja quieto: " +
      "un punto fijo. Se elige un x₀ y se aplica g una y otra vez; si g acerca los puntos entre sí " +
      "cerca de la raíz, la sucesión cae hacia ella.",
    recurrencia: String.raw`x_{n+1} = g(x_n)`,
    condicion: String.raw`|g'(r)| < 1`,
    cuandoAplica:
      "Es el método base del que salen otros: entenderlo explica Aitken, Steffensen y, en el " +
      "fondo, también Newton. La clave no es el método sino la elección de g(x).",
    orden: {
      valor: 1,
      etiqueta: "Lineal",
      nota:
        "El error se multiplica por |g'(r)| en cada paso. Cuanto más cerca de 0, más rápido; " +
        "en cuanto |g'(r)| ≥ 1 la sucesión se aleja en vez de acercarse.",
    },
    ventajas: [
      "Idea simple y muy visual: la telaraña muestra la convergencia de un vistazo.",
      "No necesita derivadas para iterar.",
      "Base conceptual de varios de los demás métodos.",
    ],
    desventajas: [
      "Una misma ecuación admite varias g(x), y no todas convergen.",
      "Requiere comprobar |g'(r)| < 1, que es una condición local.",
      "Lento frente a los métodos con derivada.",
    ],
    advertencia:
      "En la pestaña Calcular, la g(x) que el sistema propone por defecto es siempre " +
      "x − f(x)/f'(x), que resulta ser la iteración de Newton escrita de otra forma: converge " +
      "de inmediato y nunca pone a prueba la condición |g'| < 1. Por eso la demostración de aquí " +
      "usa reordenamientos elegidos a mano, donde sí se ve la diferencia entre una g que atrae " +
      "y una que repele. (Hallazgo H1 en CLAUDE.md §7.)",
    demo: "cobweb",
  },

  aitken: {
    label: "Aitken (Δ²)",
    familia: "punto-fijo",
    idea:
      "No es un método para buscar raíces, sino para acelerar una sucesión que ya converge " +
      "despacio. Mira tres términos consecutivos, estima hacia dónde van y salta directamente " +
      "a ese destino estimado.",
    recurrencia: String.raw`\hat{p}_k = p_{k+1} - \frac{(p_{k+2} - p_{k+1})^2}{p_{k+3} - 2p_{k+2} + p_{k+1}}`,
    condicion: String.raw`p_{k+3} - 2p_{k+2} + p_{k+1} \neq 0`,
    cuandoAplica:
      "Cuando tienes una sucesión de punto fijo que converge, pero tan despacio que aburre. " +
      "Se aplica encima de ella, sin cambiar el método que la generó.",
    orden: {
      valor: null,
      etiqueta: "Acelerador",
      nota:
        "No tiene orden propio: transforma la sucesión que le des. Sobre una convergencia lineal " +
        "reduce mucho el error con los mismos términos, pero si la de partida no converge, no hay nada que acelerar.",
    },
    ventajas: [
      "Aprovecha términos ya calculados: no evalúa f de nuevo.",
      "Mejora sensiblemente una convergencia lenta.",
      "Se puede aplicar sobre cualquier sucesión, no sólo de punto fijo.",
    ],
    desventajas: [
      "Depende por completo de la sucesión de partida.",
      "El denominador puede anularse y hay que protegerlo.",
      "Necesita varios términos antes de dar el primer resultado.",
    ],
    advertencia: null,
    demo: null,
  },

  steffensen: {
    label: "Steffensen",
    familia: "punto-fijo",
    idea:
      "Combina punto fijo con la aceleración de Aitken: en lugar de acelerar al final, reinyecta " +
      "el valor acelerado como nuevo punto de partida. Así consigue la velocidad de Newton sin " +
      "calcular ninguna derivada.",
    recurrencia: String.raw`\text{capa 1: } p_{k+1} = g(p_k)\quad
\text{capa 2: } a_k = \Delta^2(p)\quad
\text{capa 3: } s_k = \Delta^2(a)`,
    condicion: String.raw`g \text{ debe estar definida y los denominadores } \Delta^2 \neq 0`,
    cuandoAplica:
      "Cuando quieres velocidad parecida a la de Newton pero no tienes (o no quieres) la derivada.",
    orden: {
      valor: 2,
      etiqueta: "Cuadrático (clásico)",
      nota:
        "El Steffensen de libro es cuadrático. Esta implementación aplica Δ² en dos capas sobre la " +
        "sucesión de punto fijo, siguiendo la hoja Excel de referencia, así que su comportamiento " +
        "se lee mejor en la tabla de iteraciones que en el orden teórico.",
    },
    ventajas: [
      "Rápido sin necesitar derivadas.",
      "Sólo evalúa g, que suele ser barata.",
    ],
    desventajas: [
      "Hereda de punto fijo la dependencia de una buena g(x).",
      "Los denominadores Δ² pueden anularse.",
      "Sensible al punto inicial.",
    ],
    advertencia: null,
    demo: null,
  },

  // ── Métodos con derivada ───────────────────────────────────────────────────
  newton: {
    label: "Newton-Raphson",
    familia: "derivada",
    idea:
      "Sustituye la función por su recta tangente en el punto actual y se va a donde esa recta " +
      "corta el eje. Como la tangente aproxima muy bien a f cerca del punto, el nuevo x suele " +
      "estar mucho más cerca de la raíz.",
    recurrencia: String.raw`x_{n+1} = x_n - \frac{f(x_n)}{f'(x_n)}`,
    condicion: String.raw`f'(x_n) \neq 0`,
    cuandoAplica:
      "La opción por defecto cuando tienes la derivada y una aproximación inicial razonable. " +
      "Es el método de referencia contra el que se comparan los demás.",
    orden: {
      valor: 2,
      etiqueta: "Cuadrático",
      nota:
        "Cerca de la raíz, el número de cifras correctas se dobla en cada paso. Pero eso vale " +
        "para raíces simples: si la raíz es múltiple, baja a lineal.",
    },
    ventajas: [
      "Muy rápido cerca de la raíz.",
      "Pocas iteraciones para mucha precisión.",
      "Bien entendido y fácil de razonar.",
    ],
    desventajas: [
      "Necesita la derivada.",
      "Si f'(xₙ) ≈ 0 la tangente es casi horizontal y el salto se dispara.",
      "Puede divergir o ciclar con un x₀ malo.",
    ],
    advertencia: null,
    demo: null,
  },

  newton_modificado: {
    label: "Newton Modificado",
    familia: "derivada",
    idea:
      "Variante de Newton pensada para raíces múltiples, donde el Newton normal pierde velocidad. " +
      "Aplica la idea de Newton a la función f/f′ en lugar de a f, lo que borra la multiplicidad.",
    recurrencia: String.raw`x_{n+1} = x_n - \frac{f\,f'}{(f')^2 - f\,f''}`,
    condicion: String.raw`(f')^2 - f\,f'' \neq 0`,
    cuandoAplica:
      "Cuando sospechas que la raíz es múltiple (la curva toca el eje en vez de cruzarlo) y " +
      "Newton avanza más despacio de lo que debería.",
    orden: {
      valor: 2,
      etiqueta: "Cuadrático",
      nota: "Conserva el orden 2 incluso en raíces múltiples, que es justo donde Newton cae a lineal.",
    },
    ventajas: [
      "Mantiene la velocidad en raíces múltiples.",
      "Misma filosofía que Newton, sin sorpresas conceptuales.",
    ],
    desventajas: [
      "Necesita también la segunda derivada.",
      "Más caro por iteración que Newton.",
    ],
    advertencia: null,
    demo: null,
  },

  newton_segundo_orden: {
    label: "Newton 2do Orden",
    familia: "derivada",
    idea:
      "En vez de aproximar f por una recta, la aproxima por una parábola (dos términos de Taylor " +
      "en lugar de uno) y resuelve esa parábola exactamente. Al usar más información local, " +
      "avanza más por iteración.",
    recurrencia: String.raw`x_{n+1} = x_n + \frac{-f' + \sqrt{(f')^2 - 2f''f}}{f''}`,
    condicion: String.raw`f'' \neq 0 \quad\text{y}\quad (f')^2 - 2f''f \geq 0`,
    cuandoAplica:
      "Cuando tienes las dos derivadas y quieres menos iteraciones que Newton, aceptando pagar " +
      "más cálculo en cada una.",
    orden: {
      valor: 3,
      etiqueta: "Cúbico",
      nota: "Resolver el modelo cuadrático exacto en lugar del lineal sube el orden de 2 a 3.",
    },
    ventajas: [
      "Menos iteraciones que Newton.",
      "Usa la curvatura, no sólo la pendiente.",
    ],
    desventajas: [
      "Necesita f''.",
      "El discriminante puede salir negativo y dejar el paso indefinido.",
      "Cada iteración cuesta más.",
    ],
    advertencia:
      "Esta implementación toma siempre la rama +√ del discriminante. Lo correcto sería evaluar " +
      "las dos ramas y quedarse con la que minimiza |f|, así que en algunas funciones puede elegir " +
      "peor de lo que debería. Pendiente conocido y anotado en CLAUDE.md §4.",
    demo: null,
  },

  secante: {
    label: "Secante",
    familia: "derivada",
    idea:
      "Newton sin derivada: sustituye la tangente por la recta que pasa por los dos últimos puntos " +
      "calculados. Esa secante aproxima la pendiente usando sólo valores de f.",
    recurrencia: String.raw`x_{n+1} = x_n - \frac{f(x_n)\,(x_n - x_{n-1})}{f(x_n) - f(x_{n-1})}`,
    condicion: String.raw`f(x_n) \neq f(x_{n-1})`,
    cuandoAplica:
      "Cuando no tienes la derivada, o calcularla es caro o incómodo, pero quieres bastante más " +
      "velocidad que la bisección.",
    orden: {
      valor: 1.618,
      etiqueta: "Superlineal (≈1.618)",
      nota:
        "El exponente es la razón áurea. Más lento que Newton por iteración, pero cada iteración " +
        "cuesta la mitad: no evalúa derivada.",
    },
    ventajas: [
      "No necesita derivadas.",
      "Casi tan rápido como Newton en la práctica.",
    ],
    desventajas: [
      "Necesita dos puntos iniciales.",
      "Si f(xₙ) ≈ f(xₙ₋₁) el denominador se anula.",
      "No garantiza que la raíz siga encerrada.",
    ],
    advertencia: null,
    demo: null,
  },

  // ── Familia Newton de orden superior ───────────────────────────────────────
  chebyshev: {
    label: "Chebyshev",
    familia: "newton-superior",
    idea:
      "Toma el paso de Newton y le añade un término de corrección que usa la segunda derivada. " +
      "Ese término compensa la curvatura que la tangente ignora.",
    recurrencia: String.raw`x_{n+1} = x_n - \frac{f}{f'} - \frac{f^2 f''}{2(f')^3}`,
    condicion: String.raw`f' \neq 0`,
    cuandoAplica:
      "Cuando quieres orden 3 y tienes las dos derivadas disponibles y baratas.",
    orden: { valor: 3, etiqueta: "Cúbico", nota: "Un término más de Taylor que Newton, un orden más." },
    ventajas: ["Más rápido que Newton por iteración.", "Corrección explícita y fácil de leer."],
    desventajas: ["Necesita f''.", "Si f' es pequeño, el término (f')³ del denominador lo amplifica."],
    advertencia: null,
    demo: null,
  },

  halley: {
    label: "Halley",
    familia: "newton-superior",
    idea:
      "Aproxima la función con una hipérbola en lugar de una recta. Es el miembro más conocido de " +
      "la familia de orden 3 y suele ser el más estable de ellos.",
    recurrencia: String.raw`x_{n+1} = x_n - \frac{f}{f' - \dfrac{f''f}{2f'}}`,
    condicion: String.raw`f' - \frac{f''f}{2f'} \neq 0`,
    cuandoAplica:
      "Cuando quieres orden 3 con buen comportamiento: de los cúbicos, el más fiable en la práctica.",
    orden: { valor: 3, etiqueta: "Cúbico", nota: "Cerca de la raíz, las cifras correctas se triplican por paso." },
    ventajas: ["Orden 3 con buena estabilidad.", "Menos iteraciones que Newton."],
    desventajas: ["Necesita f''.", "Cada iteración cuesta más que la de Newton."],
    advertencia: null,
    demo: null,
  },

  super_halley: {
    label: "Super Halley",
    familia: "newton-superior",
    idea:
      "Refinamiento de Halley: reescala el paso de Newton con un factor construido a partir de f, " +
      "f′ y f″. Con las mismas evaluaciones que Halley, exprime un orden más.",
    recurrencia: String.raw`x_{n+1} = x_n - \frac{2(f')^2 - f f''}{2\left((f')^2 - f f''\right)}\cdot\frac{f}{f'}`,
    condicion: String.raw`(f')^2 - f f'' \neq 0 \quad\text{y}\quad f' \neq 0`,
    cuandoAplica:
      "Cuando buscas el máximo de velocidad por iteración y la función es suave y bien portada.",
    orden: {
      valor: 4,
      etiqueta: "Orden 4",
      nota: "Alcanza orden 4 en raíces simples con las mismas evaluaciones que Halley.",
    },
    ventajas: ["El de mayor orden del catálogo.", "No pide más derivadas que Halley."],
    desventajas: [
      "Necesita f''.",
      "Más sensible al punto inicial: a mayor orden, menos margen de error en x₀.",
    ],
    advertencia: null,
    demo: null,
  },

  ostrowsky: {
    label: "Ostrowsky",
    familia: "newton-superior",
    idea:
      "Método de orden superior que mete la corrección de curvatura dentro de una raíz cuadrada, " +
      "en lugar de sumarla como término aparte.",
    recurrencia: String.raw`x_{n+1} = x_n - \frac{f\,\operatorname{signo}(f')}{\sqrt{(f')^2 - f f''}}`,
    condicion: String.raw`(f')^2 - f f'' > 0`,
    cuandoAplica:
      "Cuando quieres orden superior y el radicando se mantiene positivo en la zona de trabajo.",
    orden: {
      valor: 3,
      etiqueta: "Orden superior",
      nota:
        "Esta variante con raíz cuadrada es de orden superior a Newton; el Ostrowski clásico de " +
        "dos pasos, que es de orden 4, está escrito de otra forma.",
    },
    ventajas: ["Convergencia rápida.", "Una sola expresión, sin dos pasos encadenados."],
    desventajas: [
      "El radicando puede volverse negativo y dejar el paso indefinido.",
      "Necesita f''.",
    ],
    advertencia:
      "El proyecto implementa la variante con signo(f') en lugar de la fórmula estándar de dos " +
      "pasos. El signo es imprescindible: sin él el método perdía el signo de f' y divergía con " +
      "x₀ negativo (bug P1, ya corregido). Reconciliar ambas formas está pendiente y acordado " +
      "como diferido — CLAUDE.md §7, punto 10.",
    demo: null,
  },

  // ── Otros ──────────────────────────────────────────────────────────────────
  von_mises: {
    label: "Von Mises",
    familia: "otros",
    idea:
      "Newton con la derivada congelada: calcula f′ una sola vez, en x₀, y reutiliza esa misma " +
      "pendiente en todas las iteraciones. Cambia velocidad por coste.",
    recurrencia: String.raw`x_{n+1} = x_n - \frac{f(x_n)}{f'(x_0)}`,
    condicion: String.raw`f'(x_0) \neq 0`,
    cuandoAplica:
      "Cuando evaluar la derivada es caro y prefieres hacer más iteraciones baratas que pocas caras.",
    orden: {
      valor: 1,
      etiqueta: "Lineal",
      nota:
        "Al no actualizar la pendiente pierde el orden 2 de Newton, pero cada iteración cuesta " +
        "una evaluación de f y ninguna de f′.",
    },
    ventajas: [
      "Una sola evaluación de la derivada en todo el proceso.",
      "Iteraciones muy baratas.",
    ],
    desventajas: [
      "Más lento que Newton en número de iteraciones.",
      "Si f′(x₀) representa mal la pendiente en la zona de la raíz, converge muy despacio o diverge.",
    ],
    advertencia: null,
    demo: null,
  },
};

/** Orden de presentación y títulos de las familias (CLAUDE.md §3). */
export const FAMILIAS = [
  { id: "intervalo", titulo: "Métodos de intervalo", claves: ["biseccion", "regula_falsi"] },
  { id: "punto-fijo", titulo: "Punto fijo y aceleración", claves: ["punto_fijo", "aitken", "steffensen"] },
  { id: "derivada", titulo: "Métodos con derivada", claves: ["newton", "newton_modificado", "newton_segundo_orden", "secante"] },
  { id: "newton-superior", titulo: "Familia Newton de orden superior", claves: ["chebyshev", "halley", "super_halley", "ostrowsky"] },
  { id: "otros", titulo: "Otros", claves: ["von_mises"] },
];

/** Todas las claves, en el orden de presentación. */
export const CLAVES = FAMILIAS.flatMap((f) => f.claves);
