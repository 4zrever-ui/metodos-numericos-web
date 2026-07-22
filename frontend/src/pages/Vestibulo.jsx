import { Link } from "react-router-dom";

/**
 * Vestíbulo (Filosofía A, VISION_PLATAFORMA.md §2): el estudiante entra y elige
 * su módulo; no cae directo en la calculadora.
 *
 * Hoy hay un módulo real y uno anunciado. El segundo se muestra deshabilitado a
 * propósito: comunica que esto es una plataforma de varios pisos, no una
 * calculadora con una portada delante.
 */
export default function Vestibulo() {
  return (
    <section className="vestibulo">
      <p className="vestibulo-intro">
        Elige un módulo para empezar.
      </p>

      <div className="vestibulo-modulos">
        <Link to="/metodos" className="modulo-card">
          <h2>Métodos Numéricos</h2>
          <p className="modulo-card-desc">
            Resolución de ecuaciones no lineales f(x) = 0 con 14 métodos:
            intervalo, punto fijo, derivada y familia Newton superior.
          </p>
          <span className="modulo-card-cta">Entrar →</span>
        </Link>

        <div className="modulo-card modulo-card--proximo" aria-disabled="true">
          <h2>Sistemas de Ecuaciones</h2>
          <p className="modulo-card-desc">
            Métodos para sistemas lineales y no lineales.
          </p>
          <span className="modulo-card-cta">Próximamente</span>
        </div>
      </div>
    </section>
  );
}
