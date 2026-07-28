import { useMemo, useState } from "react";

import { AccionesCtx, EstadoCtx } from "./moduloContexto.js";

/**
 * Proveedor del estado del módulo. Va en `ModuloLayout`, envolviendo al
 * `<Outlet/>`, para que el estado sobreviva al cambio de pestaña.
 *
 * Este archivo exporta SÓLO el componente; los contextos y el hook
 * `useEstadoModulo` viven en `moduloContexto.js` (ver el comentario de allí).
 */
export default function ModuloProvider({ children }) {
  const [estado, setEstado] = useState({});
  const acciones = useMemo(() => ({ setEstado }), []);

  return (
    <AccionesCtx.Provider value={acciones}>
      <EstadoCtx.Provider value={estado}>{children}</EstadoCtx.Provider>
    </AccionesCtx.Provider>
  );
}
