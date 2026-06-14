// ──────────────────────────────────────────────────────────────────────────
// mathNotation.js
// Normaliza la notación que escribe el usuario a la notación que el backend
// (SymPy) entiende. Convierte LaTeX, símbolos Unicode y atajos comunes a
// expresiones Python parseables.
//
// Objetivo: que el usuario pueda escribir raíz cúbica, exponentes, etc. de
// la forma que le sea natural, sin tener que saber la sintaxis exacta de SymPy.
//
// Esta función NO valida la expresión; solo la traduce. La validación real
// la hace el backend con parse_equation(). Pero al traducir bien, evitamos
// el 95% de los errores de parseo.
// ──────────────────────────────────────────────────────────────────────────

/**
 * Convierte una cadena de entrada del usuario a notación Python/SymPy.
 * @param {string} input  Lo que el usuario escribió.
 * @returns {string}      Expresión normalizada lista para el backend.
 */
export function normalizeMathInput(input) {
  if (input == null) return "";
  let s = String(input).trim();
  if (s === "") return "";

  // ── 1. Limpieza de envoltorios comunes ──────────────────────────────────
  // "f(x) = ..."  →  "..."
  s = s.replace(/^\s*[fg]\s*\(\s*x\s*\)\s*=\s*/i, "");
  // "y = ..."     →  "..."
  s = s.replace(/^\s*y\s*=\s*/i, "");
  // "... = 0" al final  →  "..."
  s = s.replace(/\s*=\s*0\s*$/i, "");

  // ── 2. Raíces en notación LaTeX ─────────────────────────────────────────
  // \sqrt[3]{1-x}  →  cbrt(1-x)         (raíz n-ésima → potencia 1/n)
  s = s.replace(/\\sqrt\s*\[\s*([^\]]+?)\s*\]\s*\{([^}]*)\}/g, (_, n, body) => {
    const nn = n.trim();
    if (nn === "3") return `cbrt(${body})`;
    return `(${body})**(1/(${nn}))`;
  });
  // \sqrt{1-x}     →  sqrt(1-x)
  s = s.replace(/\\sqrt\s*\{([^}]*)\}/g, (_, body) => `sqrt(${body})`);
  // \sqrt[3](1-x)  variante con paréntesis
  s = s.replace(/\\sqrt\s*\[\s*([^\]]+?)\s*\]\s*\(([^)]*)\)/g, (_, n, body) => {
    const nn = n.trim();
    if (nn === "3") return `cbrt(${body})`;
    return `(${body})**(1/(${nn}))`;
  });

  // ── 3. Fracciones LaTeX ─────────────────────────────────────────────────
  // \frac{a}{b}  →  ((a)/(b))
  // Se aplica repetidamente para fracciones anidadas.
  let prev;
  do {
    prev = s;
    s = s.replace(/\\d?frac\s*\{([^{}]*)\}\s*\{([^{}]*)\}/g, "(($1)/($2))");
  } while (s !== prev);

  // ── 4. Símbolos Unicode de raíz ─────────────────────────────────────────
  // ∛(1-x)  →  cbrt(1-x)      ∛ sin paréntesis  →  cbrt(...) del siguiente token
  s = s.replace(/∛\s*\(([^)]*)\)/g, "cbrt($1)");
  s = s.replace(/∛\s*([0-9a-zA-Z_.]+)/g, "cbrt($1)");
  // √(1-x)  →  sqrt(1-x)
  s = s.replace(/√\s*\(([^)]*)\)/g, "sqrt($1)");
  s = s.replace(/√\s*([0-9a-zA-Z_.]+)/g, "sqrt($1)");

  // ── 5. Atajos de raíz cúbica en texto ───────────────────────────────────
  // raiz3(x), raíz3(x), cbrt(x) ya funciona en el backend; normalizamos los alias
  s = s.replace(/ra[ií]z\s*c[uú]bica\s*\(([^)]*)\)/gi, "cbrt($1)");
  s = s.replace(/ra[ií]z3\s*\(([^)]*)\)/gi, "cbrt($1)");
  s = s.replace(/cbrt\s*\(/gi, "cbrt(");   // unifica mayúsculas

  // ── 6. Constantes y operadores ──────────────────────────────────────────
  // π  →  pi
  s = s.replace(/π/g, "pi");
  // · ×  →  *
  s = s.replace(/[·×]/g, "*");
  // ÷  →  /
  s = s.replace(/÷/g, "/");
  // − (minus unicode)  →  - (guion ASCII)
  s = s.replace(/−/g, "-");
  // ^  →  **   (SymPy acepta ^ con convert_xor, pero lo unificamos)
  s = s.replace(/\^/g, "**");

  // ── 7. Superíndices Unicode (x²  →  x**2) ───────────────────────────────
  const SUP = { "⁰": "0", "¹": "1", "²": "2", "³": "3", "⁴": "4",
                "⁵": "5", "⁶": "6", "⁷": "7", "⁸": "8", "⁹": "9" };
  s = s.replace(/([0-9a-zA-Z_)\]])([⁰¹²³⁴⁵⁶⁷⁸⁹]+)/g, (_, base, sup) => {
    const digits = sup.split("").map((c) => SUP[c]).join("");
    return `${base}**${digits}`;
  });

  // ── 8. Limpieza final ───────────────────────────────────────────────────
  // Quitar llaves sueltas que pudieran quedar de LaTeX mal cerrado
  s = s.replace(/[{}]/g, "");
  // Espacios múltiples → uno
  s = s.replace(/\s+/g, " ").trim();

  return s;
}

/**
 * Detecta si una cadena parece estar en notación LaTeX o Unicode "rara",
 * para mostrar al usuario un aviso suave de que se va a normalizar.
 * @param {string} input
 * @returns {boolean}
 */
export function looksLikeLatex(input) {
  if (!input) return false;
  return /\\(sqrt|frac|d?frac)|[∛√π²³⁴·×÷−⁰¹⁵⁶⁷⁸⁹]/.test(String(input));
}

/**
 * Devuelve una vista previa de cómo quedará la expresión tras normalizar,
 * útil para mostrar al usuario "interpretado como: ..." debajo del input.
 * @param {string} input
 * @returns {string|null}  null si no hubo cambios (no hace falta mostrar nada)
 */
export function normalizationPreview(input) {
  const normalized = normalizeMathInput(input);
  const original = String(input ?? "").trim();
  if (normalized === original || normalized === "") return null;
  return normalized;
}
