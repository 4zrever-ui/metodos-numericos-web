import { useEffect } from "react";
import { Link, Outlet } from "react-router-dom";
import { API } from "../api";

/**
 * Cascarón de toda la plataforma: cabecera de NumériCa + el contenedor .app
 * (max-width 900px) que antes ponía la calculadora. Debajo se monta el módulo
 * activo a través de <Outlet/>.
 */
export default function PlataformaLayout() {
  // G5 (warm-up), subido aquí desde la calculadora en FASE 1: al cargar el sitio
  // empuja a Render (free tier → hiberna) a despertar en segundo plano y en
  // silencio, mientras el estudiante elige módulo y lee. GET / es trivial (no
  // toca SymPy). Si falla, se traga el error: es un empujón best-effort, sin
  // banner ni mensaje. Monta una sola vez, en la raíz de rutas, así que el
  // vestíbulo juega a favor del cold-start en vez de retrasarlo.
  useEffect(() => {
    fetch(`${API}/`).catch(() => {});
  }, []);

  return (
    <div className="app">
      <header className="plataforma-header">
        <Link to="/" className="plataforma-marca">
          Numéri<span className="plataforma-marca-acento">Ca</span>
        </Link>
        <p className="plataforma-lema">Plataforma de matemática computacional académica</p>
      </header>

      <Outlet />
    </div>
  );
}
