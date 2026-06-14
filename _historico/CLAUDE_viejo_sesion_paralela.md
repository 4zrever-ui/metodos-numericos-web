# CLAUDE.md — Contexto del proyecto para Claude Code

> Este archivo lo lee Claude Code automáticamente al abrir el proyecto.
> Resume qué es el proyecto, su estado, y las reglas de trabajo.

## Qué es

Plataforma web de **métodos numéricos** para resolver ecuaciones no lineales
f(x) = 0. Pensada como recurso académico universitario (no solo calculadora).

- **Frontend:** React + Vite. Todo el UI vive hoy en un único `frontend/src/App.jsx` (~1100 líneas).
- **Backend:** FastAPI + SymPy. Calcula derivadas simbólicas (no diferencias finitas) y ejecuta 14 métodos.
- **Despliegue:** Frontend en Vercel, backend en Render (free tier, **hiberna** tras inactividad → primer request lento).

## Arquitectura del backend (respetar esta separación)

```
equation_parser  →  auto_params  →  methods/*  →  schema  →  excel_generator
```

- `core/equation_parser.py` — parsea con SymPy. Acepta `cbrt()`, `sqrt()`, `**`, `^`, multiplicación implícita.
- `core/auto_params.py` — detecta automáticamente a, b, x0, g(x), raíces por signos de f(x).
- `methods/` — un archivo por método. Todos devuelven `MethodResult`.
- `excel/excel_generator.py` — reproduce la hoja Excel de referencia celda a celda.
- `main.py` — endpoints: `/params`, `/method/{name}`, `/method/all`, `/excel/single`, `/excel/all`, `/diagnose`. Tiene `KEY_MAP` que normaliza claves de método.

## Los 14 métodos

Intervalo: bisección, regula falsi.
Punto fijo: punto_fijo, aitken, steffensen.
Derivada: newton_raphson, newton_2do_orden, secante, newton_modificado.
Familia Newton orden superior: halley, chebyshev, super_halley, ostrowsky.

## Estado matemático conocido (verificado)

- ✅ Newton, Bisección, Halley, Chebyshev, Newton Modificado, Secante: **correctos**.
- ⚠️ **Ostrowsky**: usa una variante propia con `copysign`, NO la fórmula estándar. Pendiente de corregir.
- ⚠️ **Newton 2do orden**: solo toma la rama `+√discriminante`. Debería evaluar ambas y elegir la que minimice |f|.
- ℹ️ `iteration_count = len(rows) − 1` puede confundir al contar iteraciones en la tabla.

## Reglas de trabajo (IMPORTANTE)

1. **Probar contra el backend real antes de afirmar que algo es un bug.** En esta sesión, dos "bugs" supuestos (x=1 no funciona, fallo de auto_params) resultaron falsos al ejecutar el código. Verificar siempre.
2. **No instalar MathQuill/MathLive** para el editor de ecuaciones. Se decidió usar un normalizador ligero (`mathNotation.js`) en su lugar. 200KB de dependencia no se justifican.
3. **No tocar el motor matemático del backend sin tests.** La suite de pytest valida los métodos contra la hoja Excel de referencia.
4. **Validar con `npm run build` antes de entregar cambios de frontend.** El build de Vite caza errores de sintaxis/imports.
5. El backend de Render hiberna: cualquier fetch nuevo debe contemplar el cold start (retry + aviso al usuario).

## Convenciones de estilo del frontend

- Variables CSS definidas en `index.css`: `--accent`, `--accent-bg`, `--accent-border`, `--border`, `--text`, `--text-h`, `--bg`, `--mono`. Usarlas (respetan modo claro/oscuro automáticamente).
- El canvas NO hereda variables CSS: usar la función `getGraphPalette()` que detecta `prefers-color-scheme`.

## Roadmap acordado (orden de ejecución)

1. **[HECHO]** Bloque 1 — bugs: normalizador de notación, canvas modo claro, cold-start retry, aviso raíz exacta, fix descarga Excel.
2. **[SIGUIENTE]** Estructura de navegación con react-router (para que teoría/Excel/práctica tengan dónde vivir). Hoy todo es una sola página.
3. Identidad académica: landing, encabezado institucional, `<title>` correcto (hoy dice "frontend").
4. Teoría viva con KaTeX (el backend YA genera `f_latex`, `fp_latex`, `fpp_latex` — solo falta renderizarlos).
5. Constructor de Excel paso a paso (el diferenciador único del proyecto).
6. Corregir Ostrowsky y Newton 2do orden (requiere tests).
7. Modo práctica / examen.

## Comandos

```bash
# Frontend
cd frontend && npm install && npm run dev      # desarrollo
cd frontend && npm run build                   # validar build
cd frontend && npx eslint src/App.jsx          # linter

# Backend
cd backend && pip install -r requirements.txt
cd backend && uvicorn main:app --reload
cd backend && pytest                           # tests de los métodos
```
