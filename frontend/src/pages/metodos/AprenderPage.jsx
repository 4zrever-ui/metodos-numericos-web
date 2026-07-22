/**
 * Esqueleto de FASE 1. El contenido llega en FASE 2 (VISION_PLATAFORMA.md §3).
 *
 * No se deja en blanco a propósito: una página vacía parece un bug, una que
 * dice qué vivirá aquí comunica que el edificio está en obra.
 */
export default function AprenderPage() {
  return (
    <section className="pagina-esqueleto">
      <h2>Aprender — entiende cómo funciona</h2>
      <p className="pagina-esqueleto-nota">Sección en construcción (Fase 2).</p>

      <p>Aquí vivirán:</p>
      <ul>
        <li>
          La <strong>teoría de cada método</strong>: qué es, su fórmula, cuándo
          aplica y su orden de convergencia, con las fórmulas renderizadas en
          KaTeX.
        </li>
        <li>
          Debajo, la <strong>demostración gráfica interactiva</strong> — la pieza
          estrella: eliges tus parámetros (x₀, intervalo) sobre el gráfico y ves
          paso a paso cómo converge el método con tu propia función.
        </li>
        <li>
          La prueba de concepto será el <strong>diagrama de telaraña</strong> de
          punto fijo; si funciona bien, se vuelve la plantilla para las demás
          familias (intervalo, tangentes de Newton, secante).
        </li>
      </ul>

      <p className="pagina-esqueleto-nota">
        Mientras tanto, la calculadora ya muestra teoría viva con KaTeX en la
        pestaña Calcular.
      </p>
    </section>
  );
}
