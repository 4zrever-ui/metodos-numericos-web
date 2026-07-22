import { NavLink, Outlet } from "react-router-dom";

/**
 * Cascarón del módulo "Métodos Numéricos": su título y las tres pestañas de la
 * progresión pedagógica (comprende → construye → verifica). Las pestañas viven
 * en el layout, no en las páginas, para que persistan mientras cambia el
 * contenido de abajo (<Outlet/>).
 *
 * NavLink marca sola la pestaña activa vía su render-prop `isActive`, así que
 * no hace falta llevar estado de "pestaña actual" a mano.
 */
const PESTANAS = [
  { to: "aprender",  label: "Aprender",  hint: "Entiende cómo funciona" },
  { to: "practicar", label: "Practicar", hint: "Constrúyelo tú mismo" },
  { to: "calcular",  label: "Calcular",  hint: "Verifica tu trabajo" },
];

export default function ModuloLayout() {
  return (
    <>
      <div className="modulo-header">
        <h1>Métodos Numéricos</h1>
        <p className="subtitle">Resolución de ecuaciones no lineales f(x) = 0</p>
      </div>

      <nav className="modulo-tabs" aria-label="Secciones del módulo">
        {PESTANAS.map(({ to, label, hint }) => (
          <NavLink
            key={to}
            to={to}
            title={hint}
            className={({ isActive }) =>
              isActive ? "modulo-tab modulo-tab--activa" : "modulo-tab"
            }
          >
            {label}
          </NavLink>
        ))}
      </nav>

      <Outlet />
    </>
  );
}
