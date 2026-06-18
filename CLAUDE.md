# CLAUDE.md — Métodos Numéricos Web · Documento maestro (única fuente de verdad)

> Este es el ÚNICO documento de estado del proyecto. Reemplaza y deja obsoletos
> a todos los anteriores (Archivo 00–06, TRASPASO_SESION, LEEME, versiones
> previas de CLAUDE.md). Si algo aquí contradice a otro .md viejo, manda éste.
>
> Claude Code lo lee automáticamente al abrir el proyecto.
> Última actualización: 2026-06-14 (push a origin/main + verificación en navegador en vivo).

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
- **Rama actual:** `main`. Todo el trabajo de esta sesión está en commits **locales** (nada
  pusheado). Render sirve una versión vieja hasta que se haga push (ver §7).

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

- ✅ **152/152 tests pasando.** (+2 capa endpoint G6, 2026-06-14; +3 detección de raíces G2/G7, 2026-06-17.)
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

**Frontend (integrado en esta sesión — 2026-06-14):**
- **`mathNotation.js` integrado** (commit `66e8032`): normaliza la notación de entrada
  (LaTeX `\sqrt[3]{}`, Unicode π/√/x², `^`→`**`) en TODOS los puntos de envío
  (`/method/*`, `/excel/*`, `/params`) + vista previa "Interpretado como…" bajo
  ecuación y g(x) + `fetchWithWake()` (cold-start de Render con retry/banner).
- **Teoría viva con KaTeX** (commit `9c25a5c`): f(x), f'(x), f''(x) renderizados con
  KaTeX en el **flujo individual** (usa `f_latex`/`fp_latex`/`fpp_latex` que ya envía
  `/method/*`). La recurrencia (`formula_description`) se muestra como texto plano.
  Deuda técnica anotada (§7): lazy-load de KaTeX (~260 kB).
- **Coherencia verificada B/C/D** (3 capas tabla/backend/Excel, contra backend LOCAL):
  x²−4x+5 y tan(x)−x → **cero raíces basura**; x³−2x−5 → raíz 2.0946 consistente en
  las 3 capas. (La verificación EN NAVEGADOR quedó bloqueada: el frontend apunta a
  Render, que tiene la versión vieja; hay que pushear estos commits para verla en vivo.)
- Docs reorganizados (commit `5d388fd`): este CLAUDE.md es la fuente única; los .md
  viejos están en `_historico/`.

**Frontend — SIN integrar (decisión explícita, dejado para después):**
- Canvas del gráfico adaptable claro/oscuro (`getGraphPalette`) — el gráfico ya existe
  pero con fondo oscuro hardcodeado.
- Aviso de "raíz exacta" (cuando x₀ ya es la raíz, iters=0).
- Barra de símbolos rápidos (π, √, x², ÷, ×) — el normalizador ya cubre la notación,
  faltan los botones.

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

**Ya hecho (ver §5):** ✅ Ostrowsky P1 · ✅ coherencia root=None · ✅ rendimiento Excel P2
· ✅ normalizador `mathNotation.js` + cold-start (`66e8032`) · ✅ teoría viva KaTeX (`9c25a5c`)
· ✅ coherencia B/C/D verificada (3 capas, programática) · ✅ docs reorganizados (`5d388fd`)
· ✅ `.gitignore` blindado para carpetas de trabajo (`bba1f30`)
· ✅ **push a origin/main** (los 5 commits subidos; Vercel desplegó el build nuevo; Render compatible)
· ✅ **verificación EN NAVEGADOR en vivo** (https://metodos-numericos-web.vercel.app):
  normalización `^`→`**` con vista previa, teoría viva KaTeX (f/f'/f''), raíz x³−2x−5 = 2.0946
  consistente en las 3 capas, y x²−4x+5 → panel "no aplica" sin raíz basura.

**Bugs del gráfico y estado (diagnóstico 2026-06-14):**
Diagnóstico en navegador (Claude in Chrome) contra el sitio en vivo, 14 ecuaciones representativas.
- **G1 — el gráfico NO auto-encuadraba. ✅ HECHO (2026-06-17, commit `6722e0d`).** Causa: la vista
  era fija (`{ox:0, oy:0, scale:60}` en `App.jsx FunctionGraph`), con el origen clavado en la esquina
  → ventana ~[0,13]×[−12,0] que nunca se adaptaba a la función ni a la raíz; la curva quedaba fuera en
  11 de 14 casos. Arreglo: **auto-encuadre adaptativo `computeAutoView` con escalas X/Y INDEPENDIENTES**
  (la escala única no puede mostrar seno y parábola a la vez). X centrada en las raíces (o default
  centrado si no hay); Y por muestreo de f con **recorte burdo** de extremos (asíntotas/explosiones,
  `|y|>1e4`) y **eje X siempre visible**. Reset reencuadra; zoom/drag manual intactos. Todo client-side
  (no backend, no tests). Verificado: x²+1 (parábola+mínimo), x³−2x−5, 1/x−0.5 (hipérbola centrada en
  raíz), e^x−2; sin(x)−0.5 y tan(x)−x pasaron de 0 a 3874/4209 px de curva (77%/100% del alto).
  - **Bug evalF arreglado de propina (commit `b3b085a`):** la multiplicación implícita de `evalF`
    (regex `([0-9a-zA-Z_)])(\s*)(\()`) insertaba `*` antes de TODO `(` → `sin(x)`→`Math.sin*(x)` (NaN),
    dejando en blanco la curva de toda función con paréntesis (sin/cos/tan/log/sqrt). Restringida a
    insertar `*` solo tras dígito o `)`. Explica por qué sin/tan salían en blanco en el diagnóstico
    original: eran DOS bugs superpuestos (encuadre + evaluación), no solo encuadre.
- **G2 — marcador fantasma x≈0. ✅ HECHO (2026-06-17, commit `87c4f86`).** Causa: el paso 1c de
  `generate_params` (`core/auto_params.py`) usaba el punto de mínimo |f(x)| como raíz **siempre**,
  aunque |f|≠0 → para x²+1 daba `roots_approx:[0]` y el front dibujaba el marcador. Arreglo (junto con
  G7, misma familia): el fallback 1c ahora solo se acepta si |f|<1e-6 (toca el eje de verdad), y el
  paso 1a usa la fuente única `real_roots_from_sympy`. x²+1 → `roots_approx:[]` (sin fantasma).
- **G3 — resultados rancios. ✅ HECHO (2026-06-14, commit `7b72303`).** Causa raíz: el `onChange`
  de la ecuación ([App.jsx:941]) mutaba `equation` pero no invalidaba `result`/`notice`/`graphRoots`.
  Arreglo: nuevo `handleEquationChange` que limpia `result`/`notice`/`error`/`graphRoots` al cambiar de
  ecuación + `fetchAutoParams` asienta siempre `data.roots || []`. Se conservó el append (multi-raíz de
  una misma ecuación intacto). Verificado en navegador: al cambiar de ecuación la tarjeta/teoría/marcadores
  se limpian al instante y no arrastran la raíz anterior. (Antes: raíz=1 de `cbrt(x)-1` se filtraba a 3
  ecuaciones siguientes; `cos(x)-x` mostraba marcadores de `sin(x)-0.5`.)
- **G4 — banner de cold-start "sticky". ✅ HECHO (2026-06-18, commit `bbd8391`).**
  El banner de wake/cold-start no desaparecía al cambiar de ecuación o de método: `handleEquationChange`
  y `handleMethodChange` invalidaban `result`/`notice`/`error`/`graphRoots` pero NO apagaban `waking`,
  así que el aviso de la consulta anterior (ya abandonada) quedaba pegado. Arreglo (Opción A — acordada
  con el director): `setWaking(false)` en ambos handlers ([App.jsx:813] y [App.jsx:824]). Sin
  `AbortController`. Solo frontend, sin backend ni tests. `npm run build` OK.
- **G5 — cold-start de Render contamina la experiencia. ✅ HECHO (2026-06-18, commit `4705a82`).**
  Antes: "No se pudo conectar con el backend" y requests colgadas en "Calculando…"; el retry/wake
  (4 reintentos, ~30 s) no aguantaba hasta que Render despierta (~30–60 s) y un intento sin respuesta
  no tenía timeout, así que se quedaba pegado para siempre. Arreglo (solo frontend, **NO keep-alive** —
  decisión del director; sin backend ni tests):
  - **Cambio C (`fetchWithWake`):** presupuesto de reintentos subido a ~75 s (7 reintentos, backoff
    3/6/9/12/15… con tope de 15 s) + **timeout por intento** (`AbortController`, 22 s) para que un intento
    colgado se aborte y se reintente en vez de quedarse pegado (mata el "Calculando…" eterno; es timeout
    de request, uso distinto al `AbortController` de cancelación descartado en G4) + **deadline global de
    90 s** que corta los reintentos aunque queden, acotando el peor caso (~112 s techo real). Banner de
    wake con texto honesto (~30–60 s, responde al instante mientras se siga usando; ya no promete
    inmediatez perpetua).
  - **Cambio B (warm-up):** `useEffect` al montar dispara `GET /` (trivial, sin SymPy) en segundo plano
    y en silencio para empezar a despertar Render mientras el alumno lee y escribe; si falla, se traga el error.
  - `npm run build` OK, eslint 0 errores. **Verificado en vivo** (cold-start real: Render dormido ~15 min,
    recarga + cambio de ecuación mientras despierta). **G4 quedó reconfirmado en vivo en el mismo
    cold-start** (el banner ya no se queda pegado al cambiar de ecuación/método).
- **G6 — parámetros manuales incoherentes. ✅ HECHO (2026-06-14, commit `b3bf82a`).** Antes, los
  `manualParams` (g(x), [a,b], x₀) se trataban de 3 formas: individual los usaba, "Resolver todos" en
  pantalla los ignoraba (solo enviaba `{equation}` a `/method/all`), y "Excel todos" sí los aplicaba →
  **incoherencia pantalla↔Excel** (misma entrada, resultados distintos en tabla vs Excel descargado).
  Reconocimiento backend: `/excel/all` ya era method-aware vía `_excel_params` (descarta lo irrelevante,
  el `gx` solo va a punto_fijo/aitken/steffensen); `/method/all` ya leía numéricos por runner pero no el `gx`.
  Arreglo (Opción B — unificar hacia el patrón Excel, reutilizando lógica existente): el frontend envía
  `manualParams` a `/method/all` ([App.jsx resolverTodos]); el backend inyecta el `gx` manual con el helper
  existente `_parse_gx` antes del loop de `method_all` (solo lo consumen los 3 g-methods). +2 tests de capa
  endpoint con contraste (gx convergente/divergente; intervalo bracketea/no). 149/149 pasando.
- **G7 — `/excel/all` reportaba "no tiene raíces reales" para ecuaciones que SÍ las tienen. ✅ HECHO
  (2026-06-17, commit `87c4f86`).** `x³−4x+1` (3 raíces reales) generaba paneles **"Esta ecuación no
  tiene raíces reales"** falsos. Causa: `_has_real_roots` (`excel/excel_generator.py`) filtraba con
  `s.is_real is True`, que falla en el **casus irreducibilis** (cúbicas con 3 raíces reales que SymPy
  expresa con radicales complejos → `is_real` queda en `None`). Arreglo (junto con G2): ambos usan ahora
  la fuente única **`real_roots_from_sympy`** (`core/auto_params.py`) que verifica realidad
  **numéricamente** (`|im(evalf)|<1e-9`). x³−4x+1 → 3 raíces; x²+1 → False (correcto). +3 tests
  (fuente única / G7 / G2). 152/152 pasando.
  - **Limitación conocida (aceptada):** una raíz **tangente trascendente** sin cambio de signo (que
    SymPy no resuelve y la grilla no cruza) podría perderse por el gate `|f|<1e-6` del paso 1c en
    `auto_params`. Caso rarísimo; no se complica el arreglo por él.

**Conclusión clave del diagnóstico:** el normalizador/parseo funciona bien (`^`→`**`, unicode `x²`,
LaTeX `\sqrt[3]{}`→`cbrt()`, multiplicación implícita, `sqrt/cbrt/ln/e/pi`). El problema real es el
**encuadre del gráfico (G1 ✅ ya corregido)** y la **gestión de estado (G3 ✅ ya corregido)**, NO la escritura de ecuaciones.
(Nota de método: la prueba inyectó ecuaciones por form_input, no tecleo real — reconfirmar G1 tecleando a mano.)

**Pendiente — corrección/coherencia:**
1. Taxonomía de errores: NO_REAL_ROOTS, MAX_ITER, DIVERGENCE, DIVISION_BY_ZERO,
   DERIVATIVE_ZERO, COMPLEX, DOMAIN, SINGULARITY → que tras "no convergió" el usuario sepa POR QUÉ.
2. Mensajes consistentes front/back/Excel.
3. ✅ HECHO — Verificación EN NAVEGADOR de la coherencia (2026-06-14, contra el sitio en vivo
   tras el push). Pasó: normalización, teoría viva KaTeX y coherencia (raíz correcta / sin basura).

**Pendiente — experiencia y salto académico:**
4. UX matemática restante: barra de símbolos rápidos (π, √, x², ÷, ×). El normalizador ya está integrado.
5. Canvas del gráfico adaptable claro/oscuro (el gráfico ya existe; hoy fondo oscuro hardcodeado)
   + aviso de raíz exacta (x₀ ya es la raíz, iters=0).
6. Estructura de navegación (react-router) — hoy todo es una página; necesario para que
   teoría / Excel / práctica tengan dónde vivir.
7. Identidad académica: landing, encabezado institucional, `<title>` correcto (hoy "frontend").
8. **Constructor de Excel paso a paso** — el diferenciador único del proyecto.
9. Corregir Newton 2do orden (ambas ramas del discriminante).
10. Reconciliar Ostrowsky con la fórmula estándar de 2 pasos (hoy usa la variante `copysign`,
    que funciona; reconciliación diferida — acordado con el director).
11. Modo práctica / examen.
12. ✅ HECHO — Push de los 5 commits a `origin/main` (2026-06-14). Vercel desplegó el build
    nuevo; backend de Render compatible y verificado en vivo. (PR no aplica: trabajo directo en `main`.)

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

# Backend (los imports son `from backend.X` → correr DESDE LA RAÍZ del repo, no desde backend/)
uvicorn backend.main:app --reload              # servidor (desde la raíz) — ⚠️ PENDIENTE DE VERIFICAR (deducido de los imports, no ejecutado; confirmar al tocar backend para G2)
python -m pytest backend/test                  # 149 tests (desde la raíz; `cd backend && pytest` falla: ModuleNotFoundError) — VERIFICADO
```

**Dependencias de entorno (solo dev, no en el repo):** fastapi, uvicorn, pytest, formulas, scipy.
**Sin trackear:** `validacion_c1/` (Excels de inspección).
