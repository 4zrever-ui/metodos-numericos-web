import { createContext, useCallback, useContext, useState } from "react";

/**
 * Estado del módulo "Métodos Numéricos": lo que el estudiante ha escrito
 * sobrevive al cambio de pestaña.
 *
 * Salda la deuda asumida en FASE 1: `CalcularPage` se desmonta al navegar y
 * volvía en blanco, perdiendo la ecuación y los parámetros tecleados.
 *
 * **Aviso sobre por qué existe, porque la premisa original resultó falsa.**
 * La deuda se anotó diciendo que Aprender compartiría su ecuación con
 * Practicar. Verificado en FASE 3: `AprenderPage` nunca tuvo ecuación —su
 * único estado es el método elegido— y la telaraña usa presets curados. Así
 * que esto NO comparte nada con Aprender hoy. Sirve para dos cosas reales:
 * que Calcular conserve el trabajo al navegar, y que Practicar tenga por
 * dónde entregarle una ecuación cuando exista.
 *
 * El diseño busca el diff mínimo sobre `CalcularPage`, que carga nueve bugs
 * cerrados y verificados en vivo: `useEstadoModulo(clave, inicial)` devuelve el
 * mismo par `[valor, setValor]` que `useState`, así que migrar un estado es
 * cambiar UNA línea y no tocar ninguno de sus usos. Es el mismo principio de
 * "mover, no reescribir" que se aplicó en FASE 1.
 *
 * Los contextos y el hook viven en este `.js` y el proveedor en su propio
 * `.jsx` porque ESLint (`react-refresh/only-export-components`) exige que un
 * archivo de componentes exporte sólo componentes.
 */

// Dos contextos a propósito: el valor cambia en cada actualización, pero el
// actualizador que devuelve `useState` es estable. Separarlos evita que los
// setters cambien de identidad en cada render y hagan churn en los
// `useCallback` que ya existen dentro de la calculadora.
export const EstadoCtx = createContext(null);
export const AccionesCtx = createContext(null);

/**
 * Igual que `useState`, pero el valor vive en el módulo y sobrevive a la
 * navegación entre pestañas.
 *
 * Sin proveedor alrededor se comporta exactamente como `useState`, de modo que
 * un componente migrado sigue funcionando aislado (en una prueba, por ejemplo).
 */
export function useEstadoModulo(clave, inicial) {
  const estado = useContext(EstadoCtx);
  const acciones = useContext(AccionesCtx);
  const local = useState(inicial);   // se llama siempre: las reglas de hooks no admiten condicionales

  const setCompartido = useCallback(
    (v) => {
      acciones?.setEstado((prev) => {
        const actual = clave in prev ? prev[clave] : inicial;
        const nuevo = typeof v === "function" ? v(actual) : v;
        return Object.is(nuevo, actual) ? prev : { ...prev, [clave]: nuevo };
      });
    },
    // `inicial` se omite a propósito: sólo se usa la primera vez, y meterlo en
    // las dependencias recrearía el setter cuando el valor por defecto sea un
    // literal (`{}`, `[]`), que cambia de identidad en cada render.
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [acciones, clave]
  );

  if (!acciones) return local;
  return [clave in estado ? estado[clave] : inicial, setCompartido];
}
