import katex from "katex";
import "katex/dist/katex.min.css";

/**
 * Render de una expresión LaTeX con KaTeX.
 *
 * Copia compartible del `Katex` privado de `CalcularPage`: FASE 2 necesita el
 * mismo render en las fichas de teoría, y la calculadora NO se reconecta a este
 * módulo todavía (decisión del director; migración anotada como deuda técnica).
 * Mientras tanto conviven dos copias idénticas de 9 líneas.
 *
 * `throwOnError: false` deja que KaTeX pinte el error en rojo en vez de tumbar
 * el árbol de React; el `catch` cubre además el caso de que ni eso funcione.
 */
export default function Katex({ tex, display = false }) {
  let html;
  try {
    html = katex.renderToString(tex || "", { throwOnError: false, displayMode: display });
  } catch {
    html = tex || "";
  }
  return <span className="katex-wrap" dangerouslySetInnerHTML={{ __html: html }} />;
}
