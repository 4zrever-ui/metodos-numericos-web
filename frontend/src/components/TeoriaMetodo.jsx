import Katex from "./Katex.jsx";
import { TEORIA } from "../content/teoriaMetodos.js";

/**
 * Ficha de teoría de un método.
 *
 * Sólo pinta: todo el contenido viene de `content/teoriaMetodos.js`. La
 * demostración interactiva se inyecta por `children`, para que la ficha no
 * sepa nada de canvas ni de telarañas.
 *
 * El bloque `advertencia` no es decorativo: es donde el proyecto reconoce, en
 * la cara del alumno, dónde su implementación se aparta de la fórmula de libro
 * (Newton 2do orden, Ostrowsky) o dónde la calculadora hace algo que la teoría
 * no promete (punto fijo, hallazgo H1). Una herramienta académica que esconde
 * eso enseña mal.
 */
export default function TeoriaMetodo({ clave, children }) {
  const t = TEORIA[clave];
  if (!t) return null;

  return (
    <article className="ficha">
      <header className="ficha-cabecera">
        <h3>{t.label}</h3>
        <span className="ficha-orden" title={t.orden.nota}>
          {t.orden.etiqueta}
        </span>
      </header>

      <p className="ficha-idea">{t.idea}</p>

      <div className="ficha-formula">
        <span className="ficha-etiqueta">Fórmula de iteración</span>
        <Katex tex={t.recurrencia} display />
      </div>

      {t.condicion && (
        <div className="ficha-formula ficha-formula--condicion">
          <span className="ficha-etiqueta">Condición</span>
          <Katex tex={t.condicion} display />
        </div>
      )}

      <div className="ficha-bloque">
        <span className="ficha-etiqueta">Cuándo usarlo</span>
        <p>{t.cuandoAplica}</p>
      </div>

      <div className="ficha-bloque">
        <span className="ficha-etiqueta">Orden de convergencia</span>
        <p>
          <strong>{t.orden.etiqueta}</strong> — {t.orden.nota}
        </p>
      </div>

      <div className="ficha-columnas">
        <div>
          <span className="ficha-etiqueta">Ventajas</span>
          <ul className="ficha-lista ficha-lista--pro">
            {t.ventajas.map((v) => <li key={v}>{v}</li>)}
          </ul>
        </div>
        <div>
          <span className="ficha-etiqueta">Limitaciones</span>
          <ul className="ficha-lista ficha-lista--contra">
            {t.desventajas.map((d) => <li key={d}>{d}</li>)}
          </ul>
        </div>
      </div>

      {t.advertencia && (
        <div className="ficha-advertencia">
          <span className="ficha-etiqueta">En este proyecto</span>
          <p>{t.advertencia}</p>
        </div>
      )}

      {children}
    </article>
  );
}
