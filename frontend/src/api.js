// URL del backend (FastAPI en Render, free tier → hiberna).
// Vive aquí y no dentro de una página porque la usan dos sitios: la calculadora
// (consultas reales) y PlataformaLayout (el warm-up de G5, que despierta a Render
// al entrar al sitio). Duplicar la URL en ambos es la clase de cosa que se
// desincroniza el día que cambie el host.
export const API = "https://metodos-numericos-web.onrender.com";
