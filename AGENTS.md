# AGENTS.md — Reglas para agentes de código en NumériCa

Antes de hacer nada: lee CLAUDE.md y ESTADO_ACTUAL.md completos.
CLAUDE.md es la fuente de verdad del estado técnico.

## Reglas
1. Verifica ejecutando antes de afirmar. Un doc, docstring o plan NO es evidencia.
2. Muestra el diff y espera aprobación antes de modificar un archivo existente.
3. No hagas commit ni push sin orden explícita.
4. No toques backend/methods/, backend/core/ ni backend/excel/excel_templates.py
   sin tests que cubran el cambio y sin aprobación expresa.
5. CalcularPage.jsx carga bugs cerrados (G1-G9): cada cambio ahí necesita regresión.
6. Responde con evidencia (salidas, contenidos), no con resúmenes ni interpretaciones.
7. Antes de dar por terminado: `python -m pytest backend/test` (desde la raíz),
   `npm run build` y `npx eslint src` (desde frontend/).
8. Antes de commitear documentación: `python scripts/check_chars.py`.
9. frontend/src/api.js debe apuntar a Render al commitear (nunca a 127.0.0.1).
10. No instales MathQuill/MathLive. El backend declara Python 3.11.
11. Si una premisa no se sostiene al comprobarla, para y repórtala.
