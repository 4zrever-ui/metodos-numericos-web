/**
 * Esqueleto de FASE 1. El contenido llega en FASE 3 (VISION_PLATAFORMA.md §3).
 * Es el diferenciador único del proyecto: el constructor de fórmulas paso a paso.
 */
export default function PracticarPage() {
  return (
    <section className="pagina-esqueleto">
      <h2>Practicar — constrúyelo tú mismo</h2>
      <p className="pagina-esqueleto-nota">Sección en construcción (Fase 3).</p>

      <p>Aquí vivirá el <strong>constructor de fórmulas paso a paso</strong>:</p>
      <ul>
        <li>
          Una <strong>hoja de cálculo simulada</strong> —propia, no un Excel
          embebido— donde escribes las fórmulas de cada método y el sistema te
          dice si están bien, te marca los errores y te explica por qué.
        </li>
        <li>
          Acompañamiento en pantalla para que te enfoques en construir y no en
          calcular a mano: el gráfico de la función junto a la derivada, la
          segunda derivada y el g(x) predeterminados.
        </li>
        <li>
          <strong>Ejercicios propuestos que rotan cada semana</strong>, de un
          banco que avanza por fecha.
        </li>
      </ul>

      <p className="pagina-esqueleto-nota">
        Excel real no guía ni corrige; esta simulación sí. Ese es el punto.
      </p>
    </section>
  );
}
