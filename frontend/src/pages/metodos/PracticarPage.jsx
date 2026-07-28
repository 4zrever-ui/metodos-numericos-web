import { useEffect, useState } from "react";

import "../../practicar.css";
import HojaCalculo from "../../components/HojaCalculo.jsx";
import { EJERCICIOS } from "../../content/ejercicios.js";
import { API } from "../../api";

/**
 * Pestaña PRACTICAR — "constrúyelo tú mismo" (VISION_PLATAFORMA.md §3).
 *
 * FASE 3: el constructor de fórmulas paso a paso, que es el diferenciador del
 * proyecto. El alumno elige un ejercicio, escribe las fórmulas de la fila de
 * iteración y el sistema le corrige por valor, le explica cada columna y le
 * enseña la correcta si falla.
 *
 * La plantilla de fórmulas viene del backend (`/practicar/plantilla`), no de un
 * catálogo del frontend: es la MISMA fuente que genera el Excel descargable, y
 * `test_formula_specs.py` fija que no diverjan.
 */
export default function PracticarPage() {
  const [idActivo, setIdActivo] = useState(EJERCICIOS[0].id);
  // Un solo estado con el id al que pertenece la respuesta. Así "cargando" se
  // DERIVA (no hay `setState` síncrono dentro del efecto, que React 19 marca
  // como error) y de paso una respuesta que llega tarde no puede pintarse sobre
  // otro ejercicio: mismo patrón de "último gana" que G8 en la calculadora.
  const [resultado, setResultado] = useState(null);

  const ejercicio = EJERCICIOS.find((e) => e.id === idActivo) ?? EJERCICIOS[0];
  const cargando = resultado?.id !== ejercicio.id;

  useEffect(() => {
    let vigente = true;

    (async () => {
      try {
        const r = await fetch(`${API}/practicar/plantilla`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ equation: ejercicio.equation, metodo: ejercicio.metodo, filas: 7 }),
        });
        // Un 404 NO hace fallar al `fetch`: sin esta comprobación, el cuerpo
        // `{"detail":"Not Found"}` se tomaba por una respuesta buena, `hoja`
        // salía `undefined` y la página se quedaba **en blanco y en silencio**
        // —ni tabla, ni error, ni "cargando"—. Es lo que pasa hoy contra el
        // backend desplegado, que todavía no tiene este endpoint.
        if (!r.ok) {
          if (vigente) {
            setResultado({
              id: ejercicio.id,
              error:
                r.status === 404
                  ? "El servidor respondió 404: el backend desplegado todavía no tiene el endpoint /practicar/plantilla. Practicar necesita que se despliegue el backend."
                  : `El servidor respondió ${r.status}. Inténtalo de nuevo en unos segundos.`,
            });
          }
          return;
        }

        const json = await r.json();
        if (!vigente) return;
        setResultado(
          json.error ? { id: ejercicio.id, error: json.error } : { id: ejercicio.id, datos: json }
        );
      } catch {
        // El backend hiberna en Render; se dice y ya, sin inventar reintentos.
        if (vigente) {
          setResultado({
            id: ejercicio.id,
            error: "No se pudo contactar con el servidor. Si acaba de despertar, inténtalo de nuevo en unos segundos.",
          });
        }
      }
    })();

    return () => { vigente = false; };
  }, [ejercicio]);

  return (
    <section className="practicar">
      <p className="practicar-intro">
        Aquí no se calcula: se <strong>construye</strong>. Escribe la fórmula de
        cada celda de la fila de iteración, como lo harías en una hoja de cálculo.
        El sistema comprueba que haga lo mismo que la correcta —da igual cómo la
        escribas mientras el resultado sea el mismo— y te explica qué hace cada columna.
      </p>

      <nav className="practicar-selector" aria-label="Ejercicios">
        {EJERCICIOS.map((e) => (
          <button
            key={e.id}
            type="button"
            onClick={() => setIdActivo(e.id)}
            aria-current={e.id === idActivo ? "true" : undefined}
            className={e.id === idActivo ? "practicar-ejercicio practicar-ejercicio--activo" : "practicar-ejercicio"}
          >
            {e.etiqueta}
            <small>{e.metodoLabel}</small>
          </button>
        ))}
      </nav>

      <p className="practicar-aviso">{ejercicio.enunciado}</p>

      {cargando && <p>Pidiendo la plantilla del método…</p>}
      {resultado?.error && <p className="practicar-aviso">{resultado.error}</p>}

      {resultado?.datos?.hoja && <HojaCalculo hoja={resultado.datos.hoja} filaEditable={1} />}
    </section>
  );
}
