# Traspaso de sesión — Auditoría + Bloque 1 (claude.ai → Claude Code)

> Documento para que Claude Code retome exactamente donde quedó esta sesión.
> Generado desde una conversación en claude.ai. No es una sesión resumible
> de forma nativa, por eso este resumen.

## Qué se hizo en esta sesión

### 1. Auditoría completa del proyecto
Puntuaciones acordadas:
- Correctitud matemática: 8.5/10
- Estructura académica: 5.5/10 (es una calculadora, no una herramienta de aprendizaje)
- UX: 7/10
- Robustez técnica: 8/10

Hallazgo central: hay una brecha grande entre lo que el backend genera
(LaTeX de f, f', f'', descripciones de fórmulas) y lo que el frontend muestra
(nada de eso). Material académico valioso desperdiciado.

### 2. Bloque 1 de correcciones — COMPLETADO Y VERIFICADO

Tres archivos producidos (listos para copiar a `frontend/src/`):

- **`mathNotation.js`** (NUEVO) — normalizador de notación. Convierte LaTeX
  (`\sqrt[3]{}`, `\frac{}{}`), Unicode (`∛`, `√`, `x²`, `π`) y atajos
  (`raiz3()`) a notación Python que SymPy entiende. Probado con 15 casos,
  cada salida confirmada como parseable por el backend.

- **`App.jsx`** (REEMPLAZA el actual) — integra el normalizador en TODOS los
  puntos de envío (params, resolver, resolverTodos, descargas Excel, gráfico).
  Además:
  - Canvas adaptable a modo claro/oscuro (antes fondo `#1a1a2e` hardcodeado).
  - `fetchWithWake()`: retry con backoff + banner "servidor iniciando" para
    el cold start de Render.
  - Aviso cuando x₀ ya es la raíz exacta (iters=0), antes parecía tabla vacía.
  - Vista previa "Interpretado como: …" bajo los campos de ecuación y g(x).

- **`App.css`** (REEMPLAZA el actual) — estilos para la vista previa de
  notación y el banner de cold-start. Usa las variables CSS del proyecto.

Validación hecha: `npm run build` pasa limpio (18 módulos, 0 errores).
ESLint: 0 errores (2 avisos preexistentes, no introducidos).

### 3. Hallazgos que corrigen suposiciones iniciales
- `x-1` (raíz en x=1) **SÍ funciona** en el backend. El "no funciona" de la
  captura era la g(x) en LaTeX rompiendo el parser, no la ecuación.
- La g(x) `cbrt(1-x)` para `x³+x-1` es válida pero converge LENTO
  (|g'(raíz)| = 0.716), por eso agotaba las 25 iteraciones. El error de
  notación ocultaba este problema matemático real. Buen caso de uso para la
  futura "teoría viva".

## Primer paso en Claude Code (sugerido)

1. Copiar los tres archivos del paquete a `frontend/src/`.
2. `cd frontend && npm run build` para confirmar que compila en tu entorno.
3. `npm run dev` y probar el escenario de la captura: método Punto Fijo,
   ecuación `x^3 + x - 1`, g(x) `\sqrt[3]{1-x}` → debe normalizar a `cbrt(1-x)`
   y mostrar "Interpretado como: cbrt(1-x)".
4. Empezar el Bloque 2: estructura de navegación con react-router.

## Estado del roadmap
Ver `CLAUDE.md` sección "Roadmap acordado". Bloque 1 hecho; siguiente es
react-router para dar hogar a teoría / Excel / práctica.
