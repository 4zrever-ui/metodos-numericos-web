import { Navigate, Route, Routes } from "react-router-dom";

import PlataformaLayout from "./layouts/PlataformaLayout";
import ModuloLayout from "./layouts/ModuloLayout";
import Vestibulo from "./pages/Vestibulo";
import NoEncontrada from "./pages/NoEncontrada";
import CalcularPage from "./pages/metodos/CalcularPage";
import AprenderPage from "./pages/metodos/AprenderPage";
import PracticarPage from "./pages/metodos/PracticarPage";

/**
 * El mapa de rutas de NumériCa, en un solo sitio.
 *
 *   /                     vestíbulo (elige módulo)
 *   /metodos              → redirige a /metodos/calcular
 *   /metodos/calcular     la calculadora (único con contenido real hoy)
 *   /metodos/aprender     esqueleto (Fase 2)
 *   /metodos/practicar    esqueleto (Fase 3)
 *   *                     404
 *
 * /metodos redirige a Calcular porque es lo único con contenido real hoy.
 * Cuando Aprender esté llena (Fase 2) el destino natural pasa a ser Aprender:
 * la progresión pedagógica es comprende → construye → verifica.
 */
export default function AppRoutes() {
  return (
    <Routes>
      <Route element={<PlataformaLayout />}>
        <Route index element={<Vestibulo />} />

        <Route path="metodos" element={<ModuloLayout />}>
          <Route index element={<Navigate to="calcular" replace />} />
          <Route path="calcular" element={<CalcularPage />} />
          <Route path="aprender" element={<AprenderPage />} />
          <Route path="practicar" element={<PracticarPage />} />
        </Route>

        <Route path="*" element={<NoEncontrada />} />
      </Route>
    </Routes>
  );
}
