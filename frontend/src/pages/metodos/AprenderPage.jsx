import { useState } from "react";
import "../../aprender.css";
import CobwebGraph from "../../components/CobwebGraph.jsx";
import TeoriaMetodo from "../../components/TeoriaMetodo.jsx";
import { FAMILIAS, TEORIA } from "../../content/teoriaMetodos.js";

/**
 * Pestaña APRENDER — "entiende cómo funciona" (VISION_PLATAFORMA.md §3).
 *
 * FASE 2, paso 3: la teoría de los 14 métodos ya es contenido real. La
 * demostración interactiva (telaraña de punto fijo) llega en el paso 4 y se
 * inyectará en el hueco que la ficha deja por `children`.
 *
 * Arranca en Punto Fijo porque es la base conceptual de la que salen Aitken,
 * Steffensen y —escrito de otra forma— el propio Newton, y porque es el método
 * que estrenará la demostración interactiva.
 */
export default function AprenderPage() {
  const [clave, setClave] = useState("punto_fijo");
  const ficha = TEORIA[clave];

  return (
    <section className="aprender">
      <p className="aprender-intro">
        Cada método resuelve f(x) = 0 con una idea distinta sobre cómo acercarse
        a la raíz. Elige uno para ver qué hace, con qué fórmula itera, qué
        necesita para funcionar y a qué velocidad converge.
      </p>

      <nav className="aprender-selector" aria-label="Métodos numéricos">
        {FAMILIAS.map((familia) => (
          <div className="aprender-familia" key={familia.id}>
            <span className="aprender-familia-titulo">{familia.titulo}</span>
            <div className="aprender-familia-lista">
              {familia.claves.map((k) => (
                <button
                  key={k}
                  type="button"
                  onClick={() => setClave(k)}
                  aria-current={k === clave ? "true" : undefined}
                  className={
                    k === clave ? "aprender-metodo aprender-metodo--activo" : "aprender-metodo"
                  }
                >
                  {TEORIA[k].label}
                </button>
              ))}
            </div>
          </div>
        ))}
      </nav>

      <TeoriaMetodo clave={clave}>
        {ficha.demo === "cobweb" && <CobwebGraph />}
      </TeoriaMetodo>
    </section>
  );
}
