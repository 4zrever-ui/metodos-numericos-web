import { useMemo, useState } from "react";

import { celdasAEscribir, resolverHoja, validarCelda } from "../lib/hoja.js";

/**
 * La hoja de cálculo simulada: el constructor de fórmulas paso a paso.
 *
 * Es el diferenciador del proyecto (VISION §3): Excel real no guía ni corrige;
 * esto sí. El alumno escribe la fórmula de cada celda de una fila y el sistema
 * le dice si hace lo mismo que la correcta, le explica qué debía hacer y, al
 * fallar, le enseña la fórmula canónica como pista.
 *
 * Decisiones que respeta (§5, FASE 3):
 *  - D3: corrige **por valor**, no por cadena. `B3-C3/D3` vale igual que
 *    `B3-(C3/D3)`. La comprobación va por `validarCelda`, que además compara en
 *    varios escenarios para que una fórmula no pueda colarse acertando de
 *    casualidad en la fila que toca.
 *  - D4: el envoltorio `_freeze` **no se enseña**. El backend manda la fórmula
 *    limpia; ese `IF(...)` que deja la celda en blanco tras converger es
 *    presentacional y convertiría el ejercicio en uno de lógica de Excel.
 *
 * Las filas posteriores a la que se edita se ocultan hasta completarla: ver la
 * tabla ya resuelta antes de escribir nada le quita la gracia al ejercicio.
 */

const MENSAJES = {
  correcta: "Correcta.",
  "valor-distinto": "No da el mismo resultado que la fórmula correcta.",
  "coincide-por-casualidad":
    "Da el resultado correcto en esta fila, pero no es la misma fórmula: con otros valores deja de coincidir.",
  "no-evalua": "No se puede evaluar. Revisa la sintaxis.",
  "tipo-distinto": "Devuelve un tipo distinto (texto donde se esperaba número, o al revés).",
  "canonica-invalida": "Error interno: la fórmula de referencia no evalúa.",
  "sin-canonica": "Esta celda no tiene fórmula de referencia.",
};

export default function HojaCalculo({ hoja, filaEditable = 1 }) {
  const [escritas, setEscritas] = useState({});
  const [enfocada, setEnfocada] = useState(null);
  const [rendirse, setRendirse] = useState(false);

  // La hoja resuelta con las fórmulas correctas: es contra estos valores contra
  // los que se corrige, así que se calcula una vez y no depende de lo que teclee
  // el alumno.
  const solucion = useMemo(() => resolverHoja(hoja), [hoja]);

  const aEscribir = useMemo(() => celdasAEscribir(hoja, filaEditable), [hoja, filaEditable]);

  const veredictos = useMemo(() => {
    const out = {};
    for (const celda of aEscribir) {
      const texto = escritas[celda.ref];
      if (!texto || !texto.trim()) continue;
      out[celda.ref] = validarCelda(hoja, celda.ref, texto, solucion.valores);
    }
    return out;
  }, [escritas, aEscribir, hoja, solucion]);

  const correctas = aEscribir.filter((c) => veredictos[c.ref]?.veredicto === "correcta").length;
  const completada = correctas === aEscribir.length && aEscribir.length > 0;

  const filasVisibles = (hoja?.filas ?? []).filter(
    (f) => f.k <= filaEditable || completada || rendirse
  );

  const valorMostrado = (ref) => {
    const v = solucion.valores[ref];
    if (v === "" || v === null || v === undefined) return "";
    if (typeof v === "number") {
      if (Number.isInteger(v)) return String(v);
      return Math.abs(v) < 1e-4 || Math.abs(v) >= 1e6 ? v.toExponential(4) : v.toFixed(6);
    }
    return String(v);
  };

  const claseCelda = (ref) => {
    const v = veredictos[ref]?.veredicto;
    if (!v) return "hoja-celda hoja-celda--edita";
    if (v === "correcta") return "hoja-celda hoja-celda--edita hoja-celda--bien";
    return "hoja-celda hoja-celda--edita hoja-celda--mal";
  };

  if (!hoja) return null;

  const celdaEnfocada = aEscribir.find((c) => c.ref === enfocada);
  const vEnfocada = enfocada ? veredictos[enfocada] : null;

  return (
    <div className="hoja">
      <div className="hoja-barra">
        <span className="hoja-progreso">
          {correctas} de {aEscribir.length} fórmulas correctas
        </span>
        {!completada && (
          <button type="button" className="hoja-boton" onClick={() => setRendirse((r) => !r)}>
            {rendirse ? "Ocultar la solución" : "Ver la solución"}
          </button>
        )}
        {completada && <span className="hoja-listo">Hoja completa — la iteración ya se ve abajo.</span>}
      </div>

      <div className="hoja-scroll">
        <table className="hoja-tabla">
          <thead>
            <tr>
              <th className="hoja-esquina" />
              {hoja.cabeceras.map((c) => (
                <th key={c.columna}>
                  <span className="hoja-letra">{c.columna}</span>
                  <span className="hoja-cabecera">{c.cabecera}</span>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {filasVisibles.map((fila) => (
              <tr key={fila.fila} className={fila.k === filaEditable ? "hoja-fila--edita" : undefined}>
                <th className="hoja-num">{fila.fila}</th>
                {fila.celdas.map((celda) => {
                  const editable = fila.k === filaEditable && celda.tipo === "formula";
                  if (!editable) {
                    return (
                      <td key={celda.ref} className="hoja-celda">
                        {valorMostrado(celda.ref)}
                      </td>
                    );
                  }
                  return (
                    <td key={celda.ref} className={claseCelda(celda.ref)}>
                      <input
                        type="text"
                        spellCheck="false"
                        placeholder="="
                        value={escritas[celda.ref] ?? ""}
                        onChange={(e) =>
                          setEscritas((prev) => ({ ...prev, [celda.ref]: e.target.value }))
                        }
                        onFocus={() => setEnfocada(celda.ref)}
                        aria-label={`Fórmula de la celda ${celda.ref}`}
                      />
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {celdaEnfocada && (
        <div className="hoja-ayuda">
          <span className="hoja-ref">{celdaEnfocada.ref}</span>
          <p className="hoja-explicacion">{celdaEnfocada.explicacion}</p>

          {vEnfocada && (
            <p className={`hoja-veredicto hoja-veredicto--${vEnfocada.veredicto === "correcta" ? "bien" : "mal"}`}>
              {MENSAJES[vEnfocada.veredicto] ?? vEnfocada.veredicto}
              {vEnfocada.veredicto === "no-evalua" && vEnfocada.detalle
                ? ` (${vEnfocada.detalle})`
                : null}
            </p>
          )}

          {/* La cadena canónica sólo como PISTA, y sólo tras fallar (D3). */}
          {vEnfocada && vEnfocada.veredicto !== "correcta" && vEnfocada.canonica && (
            <p className="hoja-pista">
              La correcta es <code>{vEnfocada.canonica}</code>
            </p>
          )}
          {rendirse && !vEnfocada && (
            <p className="hoja-pista">
              La correcta es <code>{celdaEnfocada.contenido}</code>
            </p>
          )}
        </div>
      )}

      {rendirse && (
        <div className="hoja-solucion">
          <span className="hoja-etiqueta">Solución de la fila {filaEditable + 2}</span>
          <ul>
            {aEscribir.map((c) => (
              <li key={c.ref}>
                <code>{c.ref}</code> <code>{c.contenido}</code>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
