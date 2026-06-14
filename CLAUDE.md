# CLAUDE.md — Métodos Numéricos Web · Documento maestro (única fuente de verdad)

> Este es el ÚNICO documento de estado del proyecto. Reemplaza y deja obsoletos
> a todos los anteriores (Archivo 00–06, TRASPASO_SESION, LEEME, versiones
> previas de CLAUDE.md). Si algo aquí contradice a otro .md viejo, manda éste.
>
> Claude Code lo lee automáticamente al abrir el proyecto.
> Última actualización: 2026-06-13.

---

## 1. Qué es el proyecto

Plataforma web **académica** para resolver ecuaciones no lineales f(x) = 0 con
14 métodos numéricos, pensada para que un estudiante **aprenda** (no solo una
calculadora). Diferencial único: exporta Excel con **fórmulas nativas reales y
editables**, no valores pegados, replicando las hojas Excel académicas de
referencia (`amburger.xlsx` = fuente de verdad para formato y lógica).

- **Frontend:** React + Vite. Hoy todo el UI vive en `frontend/src/App.jsx`. Puerto 5173.
- **Backend:** FastAPI + SymPy. Derivadas simbólicas (no diferencias finitas). Puerto 8000.
- **Despliegue:** Frontend en Vercel; backend en Render (free tier → **hiberna**, primer request lento).
- **Rama actual:** `fix/excel-audit-final`. Trabajo en commits locales (ver §7 sobre push).

---

## 2. Arquitectura del backend (respetar esta separación)

```
equation_parser → auto_params → methods/* → schema → excel_generator
```

- `core/equation_parser.py` — parseo + derivadas + lambdify. Acepta `cbrt()`, `sqrt()`, `**`, `^`, multiplicación implícita.
- `core/auto_params.py` — semillas automáticas (a, b, x0, g(x), raíces) por signos de f(x).
- `core/sympy_to_excel.py` — convierte expresiones SymPy a fórmulas de Excel.
- `methods/*` — un archivo por método; todos devuelven `MethodResult`.
- `excel/excel_templates.py` — 1 plantilla por método. `excel/excel_generator.py` — arma el workbook.
- `main.py` — endpoints: `/params`, `/method/{name}`, `/method/all`, `/excel/single`, `/excel/all`, `/diagnose`. Tiene `KEY_MAP` que normaliza claves de método.
- `test/` — suite pytest (valida contra el Excel de referencia).

---

## 3. Los 14 métodos

Intervalo: **bisección, regula falsi**.
Punto fijo: **punto_fijo, aitken (Δ²), steffensen**.
Derivada: **newton_raphson, newton_modificado, newton_2do_orden, secante**.
Familia Newton superior: **chebyshev, halley, super_halley, ostrowsky**.
Otros: **von_mises**.

---

## 4. Estado matemático (VERIFICADO — corregido respecto a notas viejas)

- ✅ **147/147 tests pasando.**
- ✅ Newton, Bisección, Halley, Chebyshev, Newton Modificado, Secante, Aitken: correctos.
- ✅ **Ostrowsky: YA CORREGIDO** (bug P1: perdía el signo de f' y divergía con x0<0).
  Fórmula final: `x − f·signo(f')/√(...)`, coherente en backend y Excel.
  (Nota: una versión vieja de este documento decía "pendiente" — era incorrecta.)
- ✅ **Coherencia root=None:** cuando `converged=False` ya NO se devuelve raíz basura
  (antes salían valores como 2.4×10²⁶¹). Las 3 capas (front/back/Excel) coinciden. `iter=-1 → 0`.
- ✅ Excel verificado: x³−2x−5 → 14 tablas; x²+1 → 14 paneles "sin raíces reales"; 0 errores.
- ⚠️ **Newton 2do orden:** solo toma la rama `+√discriminante`. Debería evaluar ambas
  y elegir la que minimice |f|. (Pendiente real, requiere tests.)

---

## 5. Lo hecho hasta hoy (resumen consolidado)

**Excel y matemática:**
- IFERROR en Aitken; metadatos f/f'/f'' en footers; Secante y Ostrowsky k=0.
- `_freeze()`: detiene iteraciones tras el primer "SÍ" (13 métodos; Steffensen excluido).
- Tabla dimensionada a la convergencia (sin filas verdes sobrantes).
- Panel explicativo en Excel cuando un método no aplica/no converge + detección "sin raíces reales".
- Steffensen: 6 `#DIV/0!` arreglados. Secante F3: IFERROR faltante.
- **Rendimiento P2:** `/excel/all` de 57s → 3s (lambdify + cachés). Eliminó el "Failed to fetch".

**Frontend (Bloque 1 de la sesión de asesoría — pendiente de integrar):**
- `mathNotation.js` (NUEVO): normaliza `\sqrt[3]{}`, `^`, Unicode (π, √, x²) → notación Python.
  Cubre la UX matemática pendiente. **Es lo más valioso a integrar; archivo independiente, no rompe nada.**
- Del `App.jsx`/`App.css` de esa sesión, integrar SOLO por piezas (NO reemplazar el actual,
  que ya tiene MethodNotice y paneles de diagnóstico): canvas adaptable claro/oscuro y
  vista previa "Interpretado como…". El resto probablemente ya existe o entra en conflicto.

---

## 6. Reglas de trabajo (IMPORTANTE)

1. **Verificar contra el código real antes de afirmar que algo es un bug.** En la asesoría,
   dos "bugs" supuestos (x=1, fallo de auto_params) resultaron falsos al ejecutar.
2. **No instalar MathQuill/MathLive.** Se usa el normalizador ligero `mathNotation.js`.
3. **No tocar el motor matemático sin tests.** Mantener 147/147.
4. **`npm run build` antes de entregar cambios de frontend.**
5. **Cold start de Render:** todo fetch nuevo contempla retry + aviso al usuario.
6. **`amburger.xlsx` = fuente de verdad** para formato y fórmulas de Excel.
7. **No reemplazar archivos a ciegas:** mostrar diff y esperar confirmación.

---

## 7. Hoja de ruta (orden acordado con el director)

**Corrección (terminar lo empezado):**
1. Verificación en navegador de casos B (x²−4x+5), C (tan x−x), D (x³−2x−5). Estábamos en B.
2. Taxonomía de errores: NO_REAL_ROOTS, MAX_ITER, DIVERGENCE, DIVISION_BY_ZERO,
   DERIVATIVE_ZERO, COMPLEX, DOMAIN, SINGULARITY → que tras "no convergió" el usuario sepa POR QUÉ.
3. Mensajes consistentes front/back/Excel.

**Experiencia y salto académico:**
4. Integrar `mathNotation.js` + UX matemática (botones π, √, x², conversión `^`→`**`).
5. Gráfico interactivo de la función (canvas adaptable claro/oscuro).
6. Estructura de navegación (react-router) — hoy todo es una página; necesario para que
   teoría / Excel / práctica tengan dónde vivir.
7. Identidad académica: landing, encabezado institucional, `<title>` correcto (hoy "frontend").
8. **Teoría viva con KaTeX** — el backend YA genera `f_latex`, `fp_latex`, `fpp_latex`; falta renderizarlos.
9. **Constructor de Excel paso a paso** — el diferenciador único del proyecto.
10. Corregir Newton 2do orden (ambas ramas del discriminante).
11. Modo práctica / examen.
12. Push / PR (nada subido aún).

**Fuera de alcance explícito:** hoja Resumen (C4).

**Deuda técnica:**
- Optimización futura: cargar KaTeX de forma diferida (lazy load) para recuperar el
  peso inicial del bundle (~260 kB extra). No urgente.

---

## 8. Comandos

```bash
# Frontend
cd frontend && npm install && npm run dev      # desarrollo
cd frontend && npm run build                   # validar build
cd frontend && npx eslint src/App.jsx          # linter

# Backend
cd backend && uvicorn main:app --reload        # servidor
cd backend && pytest                           # 147 tests
```

**Dependencias de entorno (solo dev, no en el repo):** fastapi, uvicorn, pytest, formulas, scipy.
**Sin trackear:** `validacion_c1/` (Excels de inspección).
