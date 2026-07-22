import { Link } from "react-router-dom";

/**
 * Catch-all. Con rutas client-side, sin esto una URL mal escrita deja la
 * pantalla en blanco sin explicación.
 */
export default function NoEncontrada() {
  return (
    <section className="pagina-esqueleto">
      <h2>Página no encontrada</h2>
      <p>Esa dirección no existe en NumériCa.</p>
      <p>
        <Link to="/">Volver al inicio</Link>
      </p>
    </section>
  );
}
