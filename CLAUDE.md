# CLAUDE.md — Métodos Numéricos Web · Documento maestro (única fuente de verdad)

> Este es el ÚNICO documento de estado del proyecto. Reemplaza y deja obsoletos
> a todos los anteriores (Archivo 00–06, TRASPASO_SESION, LEEME, versiones
> previas de CLAUDE.md). Si algo aquí contradice a otro .md viejo, manda éste.
>
> Claude Code lo lee automáticamente al abrir el proyecto.
> Última actualización: 2026-07-27 (FASE 2: pasos 1–4; teoría + telaraña interactiva vivas).

---

## 1. Qué es el proyecto

**NumériCa — plataforma de matemática computacional académica** (nombre decidido
2026-07-21). "Métodos Numéricos" es el nombre del PRIMER MÓDULO, no del conjunto;
ver `VISION_PLATAFORMA.md` §2 para la arquitectura de módulos.

Plataforma web **académica** para resolver ecuaciones no lineales f(x) = 0 con
14 métodos numéricos, pensada para que un estudiante **aprenda** (no solo una
calculadora). Diferencial único: exporta Excel con **fórmulas nativas reales y
editables**, no valores pegados, replicando las hojas Excel académicas de
referencia (`amburger.xlsx` = fuente de verdad para formato y lógica).

- **Frontend:** React + Vite + **react-router v7**. Puerto 5173. Desde FASE 1 el UI está
  repartido en rutas (ya NO todo en `App.jsx`, que dejó de existir):

```
frontend/src/
├── main.jsx              monta <BrowserRouter>
├── routes.jsx            el mapa de rutas, en un solo sitio
├── api.js                const API (la usan la calculadora y el warm-up)
├── index.css             variables de tema · App.css  CSS de la calculadora
├── plataforma.css        CSS del esqueleto (cabecera, vestíbulo, pestañas)
├── lib/                  (FASE 2) evalExpr.js evaluador cliente · plotCore.js canvas puro
│                                  fixedPoint.js  |g′|, órbitas y segmentos de la telaraña
├── content/              (FASE 2) gxPresets.js ecuaciones de ejemplo con sus g(x)
│                                  teoriaMetodos.js  las 14 fichas + FAMILIAS
├── components/           (FASE 2) Katex.jsx · TeoriaMetodo.jsx · CobwebGraph.jsx
├── aprender.css          (FASE 2) estilos de la pestaña Aprender
├── layouts/
│   ├── PlataformaLayout.jsx   cabecera NumériCa + .app + warm-up de G5
│   └── ModuloLayout.jsx       título del módulo + pestañas (NavLink)
└── pages/
    ├── Vestibulo.jsx · NoEncontrada.jsx
    └── metodos/  CalcularPage.jsx (ex-App.jsx) · AprenderPage.jsx · PracticarPage.jsx
```
- **Backend:** FastAPI + SymPy. Derivadas simbólicas (no diferencias finitas). Puerto 8000.
- **Despliegue:** Frontend en Vercel; backend en Render (free tier → **hiberna**, primer request lento).
- **Rama actual:** `main`, sincronizada con `origin/main` (verificado 2026-07-21).

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

**FASE 1 — Esqueleto de navegación (2026-07-22, commits `6e9eeb4` + `267b349`):**
- **react-router v7** (`6e9eeb4`) y no v6: v6 sigue en mantenimiento y declara peer
  `react >=16.8`; v7 declara `>=18` y soporta oficialmente el React 19.2 del proyecto.
  Para el API declarativo que se usa (`BrowserRouter`, `Routes`, `Route`, `NavLink`,
  `Outlet`, `Navigate`) v7 es idéntico a v6 — el salto mayor fue por los modos
  framework/data. ~20 kB gzip, sin conflictos.
- **Rutas** (`267b349`, `src/routes.jsx`): `/` vestíbulo · `/metodos` → redirige a
  `/metodos/calcular` · `/metodos/{calcular,aprender,practicar}` · `*` 404.
  `/metodos` apunta a Calcular por ser lo único con contenido real hoy; cuando
  Aprender esté llena (Fase 2) el destino natural pasa a ser Aprender.
- **Principio: mover, no reescribir.** `App.jsx` cargaba 9 bugs cerrados y verificados
  en vivo (G1–G9). Se movió con `git mv` (historial conservado) a
  `pages/metodos/CalcularPage.jsx`: de sus 1252 líneas solo cambian **32** (imports,
  nombre del componente, y la cabecera + wrapper `.app` que suben a los layouts).
  Los 9 componentes internos (`FunctionGraph` ~409 líneas, `Katex`, `Teoria`…) **NO se
  extraen todavía** — su momento es la Fase 2, cuando Aprender los reutilice de verdad.
- **Warm-up de G5 subido a `PlataformaLayout`** (decisión del director): al meter el
  vestíbulo delante, dispararlo al montar la calculadora lo habría retrasado hasta que
  el estudiante llegase a Calcular, devolviendo el cold-start que G5 costó amortiguar.
  En el layout monta al cargar el sitio → Render despierta mientras se elige módulo.
  La URL del backend se extrae a `src/api.js` para no duplicarla en dos ficheros.
- **`vercel.json`** con rewrite SPA (`/(.*)` → `/index.html`): sin él, recargar en
  `/metodos/calcular` pide ese fichero al servidor y da 404. No aparece en `npm run dev`,
  solo en producción. Va en `frontend/vercel.json` → **confirmado en vivo** tras el push:
  recarga directa en `https://metodos-numericos-web.vercel.app/metodos/aprender` sirve la
  app (antes del deploy daba 404), lo que además verifica empíricamente que el
  *Root Directory* del proyecto de Vercel es `frontend/`.
- **`index.html`:** `<title>` de "frontend" → NumériCa, `lang="es"`, meta description.
  (Cierra parte del punto 7 de la hoja de ruta.)
- **Estilos:** `src/plataforma.css` nuevo; `App.css` **no se toca**. Reutiliza las
  variables de `index.css` → hereda claro/oscuro sin trabajo extra.
- **Verificado EN VIVO tras el push** (https://metodos-numericos-web.vercel.app):
  `/`, `/metodos/aprender` y `/metodos/calcular` por recarga directa, pestaña activa
  correcta, calculadora y canvas montados, 0 errores de consola.
- **Verificado en navegador (dev):** 5 rutas + 404, redirección de `/metodos`, pestaña
  activa, 0 errores de consola, warm-up disparando desde `/`. **Regresión de la
  calculadora:** x³−2x−5 → 2.094551482 en 3 iteraciones con teoría KaTeX y tabla;
  G3 (cambiar ecuación limpia resultados) y G1 (sin(x)−0.5 encuadra al 77% del alto /
  100% del ancho — los mismos números registrados para G1) siguen vivos.
  `npm run build` OK, eslint **0 errores** (2 warnings preexistentes en el código movido).
- **Backend: cero cambios.** El front habla por URL absoluta y rutas fijas; los 152 tests
  ni se ejecutan ni se rozan.

**FASE 2 — Llenar APRENDER (en curso, arrancada 2026-07-27).**
Plan aprobado por el director: teoría de los **14 métodos** (D1) + demo interactiva
**sólo** en punto fijo (VISION §6: una visualización perfecta antes que catorce a medias).
Secuencia: (1) cimientos · (2) `gx_candidates` en `/params` · (3) teoría · (4) telaraña · (5) cierre.
Decisiones tomadas antes de escribir código: **no** reconectar `CalcularPage` a los módulos
nuevos (D2, ver deuda técnica en §7) · **sí** tocar el backend para `gx_candidates` (D3) ·
**no** subir el estado `equation` a `ModuloLayout` todavía (D4, sigue agendado para FASE 3).

Tres hallazgos del código real condicionaron ese plan (verificados, no supuestos):
- **`gx_candidates` ya existe y se estaba tirando.** `core/auto_params.py` los genera con
  `label`/`gp_abs`/`converges`/`latex`/`expr` y los ordena poniendo los convergentes primero,
  pero `/params` sólo devolvía el ganador (`gx`). Es justo el material de la lección de la
  telaraña: misma ecuación, dos g(x), una converge y otra escapa. → paso 2.
- **`formula_description` es texto Unicode, no LaTeX** (`"xₙ₊₁ = xₙ − f(xₙ) / f'(x₀)"`). El
  backend sólo da LaTeX **por ecuación** (`f`/`f'`/`f''`/`gx_latex`), nunca **por método**.
  ⇒ la teoría de Aprender es un catálogo estático escrito en el frontend; no se le pide al
  backend nada que no tenga.
- **`punto_fijo.py` se NIEGA a iterar si |g′(x₀)| ≥ 1** (`_check_applicability` devuelve
  `applicable:false` con `iterations:[]`). Correcto para una calculadora, inservible para
  enseñar: la telaraña divergente es media lección. ⇒ **la telaraña itera g(x) en el cliente**,
  no consume `/method/punto_fijo`. Ese gate NO se toca (es motor matemático con tests).
- **`FunctionGraph` no se reutiliza, y por matemática, no por código:** usa escalas X/Y
  independientes (arreglo de G1, correcto para f). En un cobweb eso es veneno: con
  scaleX ≠ scaleY la recta y = x deja de verse a 45° y se pierde toda la intuición del rebote.
  La telaraña necesita escala **isométrica** — requisito opuesto al de G1, no un flag.

**Paso 1 — cimientos (2026-07-27, commit pendiente en el momento de escribir esto).**
Tres archivos NUEVOS; **cero archivos existentes tocados** (verificado con `git status`):
- `src/lib/evalExpr.js` — evaluador de expresiones → `(x)=>number`, con caché. Traduce en
  **una sola pasada con tabla de nombres**: encadenar `.replace()` por función es una trampa
  en cuanto dos nombres comparten destino (`Abs` y `abs` → `Math.abs` daba `Math.Math.abs`).
  Entiende lo que imprime SymPy (`Abs`, `sqrt`, `exp`, `log`, `E`) y `cbrt`, que `evalF` no.
  Distingue **no compila** (`null`, expresión ininteligible) de **NaN** (fuera de dominio):
  la telaraña necesita decir "no supe leer tu g(x)" y "g(x) se escapó" con mensajes distintos.
  Lleva una **lista blanca de nombres antes de `new Function`**: tras traducir, el único
  identificador que puede quedar es `x` (es guarda de UX, no un sandbox).
- `src/lib/plotCore.js` — `makeTransform`, `niceStep`, `formatTick`, `gridLines`, **`isoView`**
  (encuadre isométrico, la pieza que garantiza la diagonal a 45°) y **`getPlotPalette`**, que
  lee las variables CSS del tema. La telaraña nace clara/oscura, y ese `getPlotPalette` es lo
  que el pendiente 5 (canvas de Calcular hardcodeado en oscuro) reutilizará en vez de
  resolverse dos veces.
- `src/components/Katex.jsx` — copia compartible del `Katex` privado de `CalcularPage`.
- **Verificación:** batería propia de **52/52** casos (los reales de la app, la salida de SymPy,
  la notación del alumno, dominio vs expresión inválida, y la no-regresión del doble mapeo).
  ESLint **0 errores / 0 warnings**. `npm run build` OK.
- **Incidente, cazado por el linter:** la primera versión apartaba los literales en notación
  científica detrás de marcadores y coló **4 bytes NUL** dentro de dos regex (`no-control-regex`).
  Reescrito sin esa maquinaria: ahora la multiplicación implícita comprueba si la letra es la
  `e` de un exponente y la respeta. Sin ese arreglo `1e-5` se evaluaba como `1*e-5` ≈ −2.28.

**Paso 2 — REDISEÑADO: D3 queda REVERTIDA, el backend no se toca (2026-07-27).**
El paso 2 iba a exponer `gx_candidates` en `/params` (D3, aprobada). Al ir a escribirlo se
verificó primero el contenido real del campo (regla 1) y **la premisa era falsa**:

| Ecuación | nº candidatos | g(x) | \|g′\| | ¿converge? |
|---|---|---|---|---|
| x³−2x−5 | 1 | x − f/f′ | 0.0 | sí |
| cos(x)−x | 1 | x − f/f′ | 0.0 | sí |
| x³−4x+1 | 1 | x − f/f′ | 0.0 | sí |
| x²−4x+5 | 0 | — | — | — |

`_generate_gx_candidates` ([auto_params.py:124]) anuncia estrategias en su docstring pero
**sólo implementó la S1** (`x − f(x)/f'(x)`). Nunca hay dos candidatos, y el único que hay
converge siempre por construcción (|g′| = 0 en la raíz). El contraste "una g converge y otra
escapa" —la lección entera de la telaraña— **no existe en esos datos**, así que exponerlos
habría añadido un array de un elemento que duplica el `gx` que `/params` ya devuelve.
**Decisión del director: abandonar el cambio de backend e ir por presets.** Backend intacto,
152 tests sin ejecutar siquiera. (De la misma verificación salió el hallazgo H1, ver §7.)

Lo construido en su lugar (dos archivos NUEVOS, cero existentes tocados):
- `src/lib/fixedPoint.js` — `derivativeAt` (diferencia central con paso escalado a |x|),
  `analyzeG` (**mide** |g′| y dice si el punto fijo atrae), `iterateG` (órbita completa con
  estados `convergió` / `escapó` / `sin-cerrar` / `no-compila`) y `cobwebPath` (la órbita
  convertida en los segmentos vertical/horizontal de la telaraña). **Itera en el cliente**,
  no vía `/method/punto_fijo`, porque ese endpoint devuelve `iterations: []` cuando
  |g′(x₀)| ≥ 1 y la trayectoria divergente es justo la que hay que dibujar.
  Los defaults (`tol` 1e-7 absoluta, `maxIter` 60) son **de dibujo, no de cálculo**: con
  convergencia lineal (|g′| ≈ 0.67) hacen falta ~40 iteraciones para 7 cifras, y cortar antes
  etiquetaba como "sin cerrar" órbitas visiblemente pegadas al punto fijo.
- `src/content/gxPresets.js` — 4 ecuaciones con sus reordenamientos. El caso canónico es
  x³−2x−5 con tres g: `cbrt(2x+5)` (|g′| = 0.152, atrae), `(x³−5)/2` (6.58, repele) y
  `5/(x²−2)` (3.68, repele). Además `cos(x)` y `e^(−x)` (|g′| < 0 → espiral en vez de
  escalera) y x²−3x+2 con UNA sola g que atrae a la raíz 1 y repele a la 2.
  **Ninguna nota afirma quién converge:** las `nota` describen el álgebra del despeje y el
  veredicto lo mide `analyzeG` sobre la g real. La página no puede mentir aunque yo me
  equivoque al curar.
- **Verificación: 35/35** casos propios — derivada numérica contra derivadas conocidas,
  integridad de los presets (`f(raíz) ≈ 0` y `g(raíz) = raíz` en los 6), el contraste
  convergente/divergente, órbitas que convergen y que escapan, casos degenerados
  (g inválida, x₀ no finito, fuera de dominio) y la forma de `cobwebPath`. ESLint 0/0,
  `npm run build` OK. (La batería del paso 1 sigue en 52/52.)
- Detalle: los módulos de `lib/` se importan **con extensión `.js`** (el resto del proyecto la
  omite). Vite la resuelve igual, y así se pueden probar con `node` a secas sin runner.

**Paso 3 — La teoría de los 14 métodos, en pantalla (2026-07-27).**
Primer paso de FASE 2 que toca un archivo existente y el primero con UI visible.
- `src/content/teoriaMetodos.js` (NUEVO) — las **14 fichas**, con el esquema fijo acordado:
  `label · familia · idea · recurrencia · condicion · cuandoAplica · orden{valor,etiqueta,nota}
  · ventajas · desventajas · advertencia · demo`. Más `FAMILIAS` (las 5 agrupaciones de §3,
  que fijan el orden de presentación) y `CLAVES`.
  **Las recurrencias copian el CÓDIGO, no el libro:** cada LaTeX reproduce la fórmula que
  implementa su `backend/methods/*.py`, para que un alumno que compare la teoría con la tabla
  de iteraciones vea lo mismo. Si código y libro discrepan, manda el código y la discrepancia
  se declara en `advertencia`.
- `src/components/TeoriaMetodo.jsx` (NUEVO) — sólo pinta; el contenido viene del catálogo y la
  demo se inyecta por `children`, así que la ficha no sabe nada de canvas.
- `src/aprender.css` (NUEVO) — estilos propios. `plataforma.css` y `App.css` **no se tocan**;
  todo se apoya en las variables de `index.css` y hereda claro/oscuro sin trabajo extra.
- `src/pages/metodos/AprenderPage.jsx` (MODIFICADO, +56/−28, diff aprobado antes de aplicarlo)
  — el esqueleto de FASE 1 pasa a selector de 14 métodos agrupado por familia + ficha
  renderizada. Arranca en Punto Fijo (base conceptual y método que estrenará la demo).
  Lo único que sobrevive del esqueleto es el principio de no mentir sobre lo que no existe:
  en punto fijo hay un hueco que anuncia la telaraña del paso 4.

**Los tres apartes "En este proyecto" (decisión de contenido, no detalle de código).**
Tres fichas llevan un bloque `advertencia` que reconoce ANTE EL ALUMNO dónde la
implementación se aparta de lo canónico. Era información que ya vivía en este CLAUDE.md
pero que el estudiante no veía por ninguna parte:
- **punto_fijo** — declara el hallazgo H1: la g(x) que propone Calcular es siempre
  x − f/f′ (Newton disfrazado), converge de inmediato y **nunca pone a prueba |g′| < 1**,
  que es toda la enseñanza del método. Por eso la demostración de Aprender usa los presets
  curados de `gxPresets.js` y **no** promete estrategias de g venidas del backend.
- **newton_segundo_orden** — declara que sólo se toma la rama +√ del discriminante (§4).
- **ostrowsky** — declara la variante `signo(f')` frente a la fórmula estándar de dos pasos,
  y que el signo es imprescindible (bug P1); reconciliación diferida (§7, punto 10).
Además, dos órdenes de convergencia se dejaron **matizados a propósito** en vez de dar un
número redondo: Steffensen (el clásico es cuadrático, pero aquí son tres capas de Δ²
siguiendo la hoja Excel) y Ostrowsky (la variante con raíz no es la de dos pasos de orden 4).
Se prefirió remitir a la tabla de iteraciones antes que afirmar un orden no verificado
**para esta implementación**.

- **Verificación: 60/60** casos propios — las 14 fichas existen, sus claves coinciden
  **exactamente** con las de `METHODS` en la calculadora (sin sobrantes ni faltantes), el
  esquema está completo en todas, y **las 38 expresiones LaTeX** (28 del catálogo + 10 de los
  presets) renderizan con **`throwOnError: true` ACTIVADO** — o sea que son válidas, no
  toleradas por el modo permisivo. Es el checkpoint que pedía el plan.
  ESLint sobre `src` completo: **0 errores** (siguen los 2 warnings preexistentes de
  `CalcularPage`; los archivos nuevos no añaden ninguno). `npm run build` OK.
  Coste en bundle: JS 521→538 kB (gzip 161→166), CSS 42→44 kB.
- Baterías de los pasos 1 y 2 sin tocar: 52/52 y 35/35.

**Paso 4 — La telaraña (2026-07-27). La pieza estrella de FASE 2.**
- `src/components/CobwebGraph.jsx` (NUEVO) — cobweb interactivo: selector de ecuación,
  botones de reordenamiento con su **|g′| medido** al lado, campo de g(x) **editable**,
  x₀ editable, paso a paso (◀ ▶), animación, reset y veredicto en prosa.
  Honra lo acordado: **escala isométrica** (`isoView`, scaleX === scaleY, con el MISMO rango
  en X e Y para que la diagonal y = x sea literalmente la diagonal del recuadro), **itera en
  cliente** con tope de 30 pasos y corte por explosión, **dibuja y explica** la divergencia en
  vez de ocultarla, y toma los g(x) de `gxPresets.js` con la paleta de `plotCore.js`.
- `src/aprender.css` — bloque de estilos de la telaraña (+168 líneas). `plataforma.css` y
  `App.css` siguen sin tocarse.
- `src/pages/metodos/AprenderPage.jsx` (MODIFICADO, **+2/−10**): el marcador del paso 3 pasa a
  `{ficha.demo === "cobweb" && <CobwebGraph />}`. El archivo existente menos tocado de la fase.
  El diff se verificó ANTES de aplicarlo montando el componente en temporal y devolviendo el
  archivo con `git checkout`, para que lo mostrado fuese el diff real y no una promesa.

**Verificación (sin capturas de pantalla — ver limitación abajo).** Se auditaron los píxeles
del canvas clasificándolos por color: **95–97 % de los píxeles de la órbita caen en tramos
rectos verticales u horizontales**, o sea que lo dibujado es de verdad una escalera contra la
diagonal y no una curva cualquiera. Seis casos, **en claro y en oscuro**:

| Caso | Resultado | Trazos |
|---|---|---|
| `cbrt(2x+5)` | converge a 2.0945 en 5 iter | 10/10 |
| `(x³−5)/2` | **escapa** (681 px en rojo) | 12/12 |
| `5/(x²−2)` | ni cierra ni escapa: ciclo | 60/60 |
| `cos(x)` | converge a 0.7391 en 23 iter (espiral) | 46/46 |
| `e^(−x)` | converge a 0.5671 en 14 iter (espiral) | 28/28 |
| `x²−3x+2` desde 0.5 | converge a 0.9998 en 18 iter | 36/36 |

Más los límites: g(x) inválida (aviso + sin órbita), x₀ no numérico (campo marcado), y g(x)
escrita a mano (`sqrt(2x+5)` → 3.4495, avisando de que |g′| se midió en x = 2 y no en la raíz).
ESLint `src` **0 errores**, `npm run build` OK (JS 538→551 kB, CSS 44→47 kB).

**Los tres fallos encontrados y corregidos durante la verificación** (los tres habrían pasado
inadvertidos a ojo — quedan escritos porque son la clase de error que arruina esta pieza):
1. **Media telaraña sin dibujar (unidades trazos vs iteraciones).** El contador lo delató:
   *"30 / 60 trazos"*. `paso` se cuenta en **TRAZOS** y `MAX_PASOS` en **ITERACIONES**, y
   `cobwebPath` genera **dos trazos por iteración**; inicializar `paso = MAX_PASOS` dibujaba
   la mitad de las órbitas largas. En el caso convergente no se notaba porque 30 > 18 y
   quedaba recortado por el `Math.min`. Arreglo: `paso === null` significa "la órbita entera",
   eliminando la confusión de unidades en vez de parchear el número.
2. **"No se ha cerrado" en órbitas que sí convergen (tolerancia vs tope de iteraciones).**
   Con el tope pactado de 30 pasos, una convergencia lineal de |g′| ≈ 0.67 (`cos x`,
   `x²−3x+2`) necesita ~40 iteraciones para 7 cifras, así que el veredicto declaraba
   "no se ha cerrado" en órbitas visiblemente pegadas al punto fijo. Se respetó el tope y se
   bajó la tolerancia a **1e-4**, que es ~1/100 de píxel en un encuadre típico: invisible.
   **Consecuencia registrada:** con esa tolerancia mostrar 9 decimales de la raíz **sería
   falso** (en convergencia lineal el error real es varias veces el último paso), así que el
   veredicto muestra **4 decimales** y remite a Calcular para la precisión del método. Se ve
   en `x²−3x+2`, que reporta honestamente 0.9998 y no 1.
3. **Canvas con los colores del tema anterior.** Al cambiar de tema el lienzo se quedaba
   blanco sobre página oscura. **No era del componente:** se registró un listener propio
   directamente en la página y también recibió **cero** eventos, lo que prueba que el emulador
   CDP no despacha el `change` de `matchMedia` aunque `mq.matches` sí cambie (un navegador real
   sí lo despacha). Aun así se reforzó con `focus` y `visibilitychange` —sin temporizadores—
   porque un lienzo con la paleta equivocada es un fallo muy visible; verificado que el fondo
   pasa de blanco obsoleto a `rgb(22,23,29)`.

**G11 — el punto fijo marcado salía del preset, no de la g dibujada (corregido el mismo día).**
Detectado por el director probando en el navegador, no por la auditoría de píxeles.
- **La ruta de reproducción reportada NO era la real, y conviene que conste** para que nadie
  la vuelva a investigar: se reportó como "escribo una g personalizada y luego cambio el
  selector de ecuación". Reproducido paso a paso, **eso ya funcionaba**: `cambiarEcuacion`
  repone la g del preset (`cbrt(2*x+5)` → `cos(x)`, veredicto y |g′| coherentes).
- **El mecanismo real es el orden inverso:** elegir la ecuación y **luego** teclear. Ahí la g
  personalizada manda —y debe mandar, escribir la propia es media lección— pero **nada en la
  pantalla lo decía** (ningún botón de reordenamiento quedaba resaltado, sin más pista) y,
  peor, el canvas seguía marcando el punto fijo en `preset.raiz`. Con `sqrt(2*x + 5)` sobre
  x³−2x−5, el disco se pintaba en 2.0945: **un punto que ni está sobre la curva dibujada ni es
  el límite de la órbita** (que converge a 3.4495).
- **Misma familia que G3** (Fase 0): cambiar una entrada sin invalidar el estado que depende de ella.
- **Arreglo, en la causa y no en el síntoma:** nuevo `puntoFijo`, derivado de **la g que se
  dibuja**: la raíz del preset si esa g la deja quieta; si no, el límite al que llegó la órbita;
  y si no hay ninguno, **no se marca nada**. El |g′| se mide ahí. Además la UI declara quién
  manda: etiqueta "Tu g(x) — es la que está activa", campo resaltado y aviso explicando que el
  punto fijo y el |g′| son los de su g, no los de la ecuación mostrada.
- **Evidencia de que no es cosmético:** en ese caso el |g′| pasó de **0.3333** (= g′(2), el
  sitio equivocado) a **0.2899** (= 1/√(2·3.4495+5), la derivada en el punto fijo real).
- Verificado: cos(x)−x desde cero (coherente) · cúbica + g personalizada (aviso, |g′| correcto)
  · cambio de preset con texto escrito (campo repuesto) · g que escapa `x²` desde x₀=2
  (**sin marcador**, |g′|=4.0000 en x=2 con aviso de criterio local) · g inválida.
  ESLint 0/0, `npm run build` OK.

**G12 — la telaraña rechazaba notación que el resto de la aplicación acepta (2026-07-27).**
Reportado por el director como *"escribo `x**2 -2` y responde «No consigo interpretar esa
g(x)»"*, con una secuencia exacta: cúbica, x₀=2, borrar el campo, elegir un reordenamiento y
luego teclear.
- **La secuencia reportada NO reproduce** (verificado paso a paso en el navegador): con
  `x**2 -2` en ASCII puro la órbita sale bien, y el estado previo de haber elegido un
  reordenamiento no influye. `compileExpr("x**2 -2")` devuelve función en `node` también.
- **La causa real son los caracteres, no la sintaxis.** `CobwebGraph` pasaba el texto directo
  a `compileExpr`, **saltándose `mathNotation.js`** —el normalizador que la calculadora usa
  desde `66e8032`—. Medido:

  | Entrada | ¿Compilaba? | Tras normalizar |
  |---|---|---|
  | `x**2 -2` (ASCII) | sí | sí |
  | `x**2 −2` (**menos U+2212**) | **no** | sí |
  | `x² - 2` (superíndice) | no | sí |
  | `2×x - 2` | no | sí |
  | `g(x) = x**2 - 2` | no | sí |

  El menos U+2212 es **el que este proyecto usa en toda su documentación y en las fichas de
  teoría**, así que sale solo al copiar y pegar: es el sospechoso número uno de lo que se vio.
- **Arreglo:** la g(x) se normaliza con `normalizeMathInput` antes de evaluarla, y se muestra
  "Interpretado como …" con `normalizationPreview`, el mismo patrón que la calculadora. La
  comparación con los reordenamientos también usa la forma normalizada, para que escribir a
  mano `x²` en vez de `x**2` siga contando como ese reordenamiento (y no dispare el aviso de
  g personalizada). **Regla 2 respetada:** se reutiliza el normalizador ligero, no se instala nada.
- **Regresión comprobada:** los 6 reordenamientos de los presets pasan por el normalizador
  **sin cambiar** (`normalizeMathInput(expr) === expr`) y evalúan idéntico en 4 puntos cada uno.
- **Limitación conocida:** el normalizador no cubre el guion corto U+2013 ni el asterisco
  Unicode U+2217; con esos la telaraña sigue diciendo que no entiende. Ampliarlo tocaría
  `mathNotation.js`, que comparte con la calculadora, y no se hizo aquí.
- Verificación: **14/14** casos nuevos (`smoke4`), más las baterías previas 52/52, 35/35, 60/60.

**Legibilidad de la telaraña (2026-07-27, pedido por el director).** Dos ajustes, sin tocar
la matemática ni el flujo:
- **Rótulo de la curva al pasar el ratón.** Sobre el lienzo, si el puntero está a ≤ 12 px de
  la curva, aparece `g(x) = … (x, g(x))` con el punto marcado. El estado del cursor vive en
  una **ref, no en estado de React**: cambia con cada píxel de movimiento y no debe provocar
  un render por cada uno. El ratón y el dibujo comparten la misma vista (`vistaDe`), porque si
  cada uno calculara la suya el puntero señalaría un sitio y la curva estaría en otro.
- **El punto fijo ahora se lee.** Antes era un disco de 5 px sin etiqueta, perdido entre la
  rejilla y la curva. Ahora lleva halo del color del fondo, borde de contraste y la etiqueta
  `punto fijo x* = …` **a la derecha, no encima**: centrada arriba tapaba justo la parte donde
  se amontona la escalera al converger. La etiqueta de x₀ pasa de `x₀` a `x₀ = valor`, con
  fondo, para no pelearse con los números del eje.
- **Efecto medido en la auditoría de píxeles:** el porcentaje de órbita "en tramos rectos" baja
  de ~97 % a 80-94 % **porque el clasificador cuenta el texto de las etiquetas como órbita**
  (son del mismo color) y las cajas tapan unos pocos píxeles de trazo. El sobrecoste es fijo
  (~60 px), así que se nota en órbitas cortas (caso `cbrt`, 437 px) y no en las largas
  (caso `5/(x²−2)`, 2186 px → 94.5 %). No es una regresión del dibujo: **la métrica dejó de ser
  comparable con la del paso 4**, y conviene recordarlo antes de leerla como un empeoramiento.
- Verificado en claro y en oscuro: cursor `crosshair` sólo sobre la curva, el rótulo aparece
  (5355 px cambian), se borra al alejarse dentro del lienzo y al salir de él. (Nota de método:
  disparar `mouseleave` a mano NO funciona —React lo sintetiza desde `mouseout`—; el primer
  intento de prueba dio un falso fallo por eso.)

**G13 — "converge" y "repele" a la vez cuando x₀ ya ERA el punto fijo (2026-07-28).**
Señalado como rareza al cerrar el paso 4 y examinado después a petición del director. Al
mirarlo en el navegador no era una rareza: eran **tres afirmaciones falsas** en el sitio donde
vive la lección del método. Con `g(x) = x²−2` y x₀ = 2 (y g(2) = 2 exactamente) se leía:
```
Converge a x ≈ 2.0000 en 1 iteraciones. La escalera se cierra sobre el punto fijo.
|g′| = 4.0000 medido en el punto fijo → mayor o igual que 1, el punto fijo repele.
```
- **No "converge":** la iteración no llegó a ningún sitio, empezó ya encima.
- **No hay escalera:** la órbita tiene UN punto y de sus dos trazos uno mide cero
  (`{x1:2,y1:2,x2:2,y2:2}`); lo dibujado es una raya vertical.
- **"1 iteraciones":** error de concordancia, visible.
- Y lo peor: un alumno que acaba de leer que |g′| < 1 es EL criterio ve el criterio violado y
  el método "convergiendo" en la misma pantalla.
**Arreglo:** el caso degenerado (`orbita.points.length === 1`) tiene mensaje propio, que lo
nombra y lo convierte en lección — *"x₀ coincide justo con el punto fijo… que la iteración se
quede quieta no significa que el método converja: significa que has empezado justo encima.
Apártate un poco (prueba x₀ = 2.01) y verás la órbita alejarse"*. El consejo **está verificado**:
desde 2.01 la órbita escapa en 8 pasos. Si el punto fijo atrae, el aviso cambia y no alarma.
Plural corregido de paso. Es de la familia del pendiente 5 ("aviso de raíz exacta"), resuelto
aquí sólo para la telaraña; en la calculadora sigue abierto.
Verificado: repulsor degenerado · el consejo x₀=2.01 · atractor degenerado (`x/2` desde 0) ·
convergencia normal (5 y 23 iteraciones, plural correcto).

**Incidente de método (importante para futuras verificaciones): el dev server sirvió código
obsoleto.** Tras restaurar un archivo con `Copy-Item` (al separar dos commits), el vigilante de
Vite dejó de ver los cambios de ESE fichero: el arreglo estaba en disco y el navegador seguía
ejecutando la versión anterior **incluso tras recargar**. Se detectó porque el texto en pantalla
no cambiaba; se confirmó pidiendo el módulo al propio servidor
(`fetch('/src/components/CobwebGraph.jsx')` → no contenía el arreglo) y se resolvió tocando la
fecha del fichero. **Riesgo real:** una verificación en navegador puede estar validando código
viejo sin avisar. Ante un cambio que "no se ve", comprobar primero que el servidor lo sirve.

**Jerarquía visual de la telaraña (2026-07-28, revisión del director en vivo).** Principio que
fija el director: **g(x) es el protagonista**; diagonal, escalera, marcadores y etiquetas la
acompañan sin taparla ni competir con ella. Dos cambios, ningún CSS nuevo:
- **La etiqueta del punto fijo pasa a ser a demanda.** Antes estaba siempre visible y tapaba la
  escalera justo donde converge, que es lo que hay que leer. Ahora, por defecto, sólo el disco;
  la caja aparece al señalar el marcador (cursor `pointer`, disco algo mayor) y se puede
  **clavar con un clic** para no tener que sostener el ratón. Mismo patrón que el rótulo de g(x)
  del cambio anterior. En la detección **el marcador manda sobre la curva**: está justo encima
  de ella, así que comprobar la curva primero lo haría inseñalable.
- **Botón "Ajustar vista"** (no zoom con rueda: eso sigue aplazado a FASE 4, §7). Reutiliza la
  lógica de límites que ya existía, aplicada a un subconjunto de puntos. El rango sigue siendo
  **el mismo en X y en Y**, así que `isoView` deriva un `scale` único y **la isometría es
  estructural**, no una comprobación que se pueda olvidar. Se reinicia al cambiar g(x), x₀ o
  ecuación (familia de G3: estaba ceñido a una órbita que ya no existe).

**Corrección del diagnóstico de partida (queda escrito porque la medición desmintió a los dos).**
El síntoma se describió como *"toda la escalera se amontona en una esquina diminuta"*. Medido,
**la órbita ya ocupaba el 62–82 % del alto**: no era eso. Lo que sí resultaba invisible eran
**los últimos pasos** de las convergencias cerradas, sub-píxel con el encuadre completo. El
botón los amplía **47× a 87×**:

| Caso | Órbita antes | Con "Ajustar vista" |
|---|---|---|
| `cbrt(2x+5)` convergente cerrado | 38 % × 82 % | **69 % × 69 %** |
| `cos(x)` oscilante | 37 % × 62 % | **56 % × 84 %** |
| `(x³−5)/2` divergente | 37 % × 82 % | 40 % × 85 % |

**Por qué el criterio se bifurca cola/cabeza.** "Encuadrar donde converge la órbita" sólo
funciona si la órbita converge. En la divergente la cola está en el infinito: aplicar el
criterio literal daba un span de **8.9e8** —alejarse ocho órdenes de magnitud, peor que no
tocar nada—. Así que: **cola** (segunda mitad de la órbita) si convergió; **cabeza** (los
primeros 4 pasos, cuando todavía está junto al punto fijo y se la ve empezar a huir) si escapó
o entró en ciclo. Por eso la fila divergente de la tabla apenas cambia: es lo correcto.

Verificado en claro y en oscuro, con la secuencia completa de la etiqueta (reposo oculta →
señalar aparece → alejarse desaparece → clavar persiste → clic fuera desaparece, 0 píxeles
residuales) y los tres casos del botón. Baterías 52/52, 35/35, 60/60, 14/14. ESLint `src`
0 errores, `npm run build` OK (JS 551→555 kB).

**Limitación de la verificación (importante):** **no hay capturas de pantalla** de ninguna
parte de FASE 2. El panel del navegador debe estar visible para que la página componga frames
y no lo estaba, así que todo lo anterior es **medición del DOM y de los píxeles del canvas**,
no inspección visual. Queda comprobado *qué* se dibuja y *dónde*; el juicio estético (grosor
del trazo, ritmo de la animación, si el punto fijo se pierde sobre la rejilla) es del director.

---

**FASE 3 — Llenar PRACTICAR (en curso, arrancada 2026-07-28).**
El constructor de fórmulas simulado. Antes de planear se verificó el código real; los
hallazgos cambiaron dos premisas del plan (ver también H2 y H3 en §7):
- **El backend SÍ tiene las fórmulas correctas, pero no como dato.** `to_excel_formula(expr,
  "B3")` ([sympy_to_excel.py:175]) es pura, y las plantillas codifican la estructura celda a
  celda (Newton: `C=f(B)`, `D=f'(B)`, `E=B-(C/D)`, `F=ABS((E-B)/E)*100`,
  `G=IF(F<0.00001,"SI","NO")`). Pero `/excel/*` devuelve **binario**: ningún endpoint las
  expone.
- **El `_freeze` NO estorba** (sondeo D2, ejecutado): con `k=0` es la identidad, así que la
  **fila k=0 ya contiene las fórmulas limpias**, y donde aparece envuelve a la fórmula sin
  entrelazarse (es su tercer argumento). Salvedad: en Bisección la actualización del intervalo
  (`IF(E2*F2<0,B2,C2)`) no existe en k=0 —ahí `a` y `b` son literales— y sólo aparece desde
  k=1, ya envuelta.
- **No hay evaluador de fórmulas de Excel en el proyecto** (H2, caso 2).
- **La premisa de la deuda de estado era falsa** (H2, caso 3).
- **Lo que VISION §3 daba por reutilizable, no lo es:** `FunctionGraph` es privado dentro de
  `CalcularPage`, no exportado, con fondo `#1a1a2e` cableado; `CobwebGraph` no acepta props y
  está atado a `GX_PRESETS` y a punto fijo. Sí sirven tal cual `plotCore`, `evalExpr`,
  `fixedPoint`, `Katex` y `teoriaMetodos`. Y ojo: **`/params` no devuelve derivadas**;
  `/analyze` da f y f′ pero **no f″**; sólo `/method/*` da las tres.

**Decisiones del director (2026-07-28):** D1 ejercicios = **conjunto curado en el frontend** ·
D2 = **módulo de especificación aparte, sin tocar `excel_templates.py`**, con un test que
construya la hoja en memoria y verifique la coincidencia (por H3) · D3 = validar por **valor
numérico**, con la cadena canónica como pista · D4 = **no** enseñar el `_freeze` (es
presentacional según su propio docstring) · D5 = **Newton y Bisección** primero.

**Decisiones añadidas tras la auditoría del bloque (2026-07-28):**
- **D6 — el alumno edita la fila k=1**, no la k=0. Es la única opción funcional: en k=0 hay
  literales (x₀, a₀, b₀) y, en Bisección, dos celdas vacías, así que no serviría como
  ejercicio de "completa la fórmula".
- **D7 — 9 escenarios de sacudida en `validarCelda`.** Aprobado con el criterio explícito de
  "mejor pecar de más verificación que menos", después de comprobar que un factor único era
  insuficiente (ver H4). Se ajustará **sólo con datos reales de uso**, no por intuición.

**Paso 3 — motor de celdas (2026-07-28).** `src/lib/celdas.js` (NUEVO, cero archivos
existentes tocados). `evaluarFormula`, `referenciasDe` y `compararFormulas`.
- **No reutiliza `evalExpr`, y no por pereza:** aquel evaluador exige que el único
  identificador sea `x`, así que rechaza `B3` de plano, y no sabe de `IF`, ni de cadenas, ni
  de comparaciones — que es justo lo que distingue una hoja de una expresión. Comparte su
  enfoque (traducir a JS y ejecutar con lista blanca), no su código.
- **Verificación: 26/26**, y las fórmulas de prueba son **las que la plantilla escribe de
  verdad**, volcadas ejecutando `NewtonRaphsonTemplate` y `BiseccionTemplate` en memoria — no
  inventadas. Incluye el envoltorio `_freeze`, que evalúa bien aunque no se enseñe.
- **Dos fallos propios cazados antes de commitear**, ambos de la familia del incidente de los
  bytes NUL de FASE 2: restauraba las cadenas con `/(\d+)/g`, que habría machacado el
  `0.00001` del criterio de convergencia; y encadenar el reemplazo de operadores convertía el
  `!==` recién creado en `!======`. Hay un caso de prueba para cada uno.

**Paso 1 — estado del módulo: la deuda de FASE 1, saldada (2026-07-28).**
Ahora lo que el estudiante escribe sobrevive al cambio de pestaña.
- `src/context/moduloContexto.js` (NUEVO) — los dos contextos y el hook `useEstadoModulo`.
  `src/context/ModuloProvider.jsx` (NUEVO) — sólo el proveedor. **Van separados porque ESLint
  (`react-refresh/only-export-components`) rechaza que un `.jsx` exporte a la vez un
  componente y un hook**; el primer intento, con todo junto, dio error.
- **Dos contextos a propósito:** el valor cambia en cada actualización, pero el actualizador
  de `useState` es estable. Separarlos evita que los setters cambien de identidad en cada
  render y hagan churn en los `useCallback` que ya existen dentro de la calculadora.
- **El diseño busca el diff mínimo**, porque `CalcularPage` carga nueve bugs verificados en
  vivo: `useEstadoModulo(clave, inicial)` devuelve **el mismo par que `useState`**, así que
  migrar un estado es cambiar UNA línea y **ninguno de los 33 usos de `equation` se toca**.
  Es "mover, no reescribir", como en FASE 1. Sin proveedor alrededor se comporta como
  `useState`, de modo que el componente sigue funcionando aislado.
- **Alcance acordado:** al módulo van la ecuación, el método, los parámetros manuales, el
  resultado, el aviso, los autoParams y las raíces del gráfico. Se quedan **locales** lo
  transitorio (cargando, error de red, banner de cold-start, panel desplegado) y **todo el
  bloque de "Resolver todos"**, que es pesado y se recalcula.
- Ficheros existentes tocados: `ModuloLayout.jsx` (+8/−2, envuelve el `<Outlet/>`) y
  `CalcularPage.jsx` (**+18/−7, un solo bloque**). Diff mostrado y aprobado antes de aplicarlo.

**Verificación en navegador (batería de regresión, dev server + backend de Render):**

| Prueba | Resultado |
|---|---|
| **La ecuación sobrevive** Calcular → Aprender → Calcular | ✅ `cos(x) - x` intacta; el método también |
| **El resultado sobrevive** al navegar | ✅ raíz 2.094551482 sigue ahí |
| **G3** — cambiar ecuación limpia resultados | ✅ y **no resucita** al volver a navegar |
| **G1** — encuadre de `sin(x)-0.5` | ✅ **77 % del alto, 100 % del ancho** — el baseline exacto |
| **G8** — último gana | ✅ consulta abandonada no deja resultado rancio; la nueva da 0.7390851332 |
| Consola | ✅ 0 errores (con búfer limpio) |

**G4 no se pudo reproducir y conviene decirlo:** su síntoma exige que Render esté dormido, y
estaba caliente. Lo que sí es verificable: **`waking` NO se migró** —sigue siendo `useState`
local— así que el camino de código del banner no lo toca este cambio. Igual `reqIdRef` (G8),
que es una ref y tampoco se tocó.

**Nota de método:** los dos errores de consola que aparecieron (`Failed to reload
ModuloContext.jsx`) eran **entradas antiguas del búfer**, del momento en que se borró ese
archivo al separarlo en dos. Se confirmó abriendo el panel con el búfer limpio: cero errores.

**Paso 2a — `FunctionGraph` extraído, sin tocar una línea de su cuerpo (2026-07-28).**
VISION §3 da por reutilizable este gráfico en Practicar, pero era **privado** de
`CalcularPage` y no estaba exportado: no había forma de usarlo desde otra página.
- `src/components/FunctionGraph.jsx` (NUEVO) · `CalcularPage.jsx` **+1/−414**: una línea de
  import y el bloque fuera. Ningún otro punto del archivo cambia.
- **El paso 2 se partió en dos por decisión propia, y la razón es metodológica:** mover el
  componente y cambiarle la paleta son cambios de naturaleza distinta, y **G1 se venía midiendo
  POR EL COLOR de la curva** (`#a78bfa`). Haciéndolos a la vez no habría forma de demostrar
  que el traslado fue fiel. Así que 2a es traslado puro —el gráfico sigue oscuro en ambos
  temas, igual que antes— y el tema es 2b.
- **Garantía de fidelidad:** el traslado se hizo **con un script**, no a mano, y se comparó
  línea por línea: **414/414 idénticas**. El `export default FunctionGraph;` va **al final del
  archivo** en vez de convertir la declaración en `export default function`, precisamente para
  que esa igualdad sea exacta y no "exacta salvo una línea". (El `export` es lo único que la
  extracción exige de verdad: el primer intento sin él no compilaba.)
- **G1 verificado tras extraer:** `sin(x)-0.5` → **77 % del alto, 100 % del ancho**, el
  baseline documentado al dígito; `tan(x)-x` → 100 %/100 %, también como está registrado;
  cúbica → 77 %/100 %. Fondo oscuro intacto. Consola 0 errores. ESLint 0 errores, build OK.
- Incidencia sin relación con el cambio: el dev server del director se cayó a mitad de la
  verificación (5173 sin responder). Se levantó uno con `.claude/launch.json` —conservado en
  FASE 2 justo para esto— y se repitió la medición completa.

**Paso 2b — el gráfico deja de ser una caja oscura fija (2026-07-28).**
Cierra el **pendiente 5** de la hoja de ruta ("canvas del gráfico adaptable claro/oscuro"),
abierto desde antes de FASE 1.
- Los **17 colores cableados** salen de la paleta del tema vía `getPlotPalette` (la misma
  función que estrenó la telaraña en FASE 2, paso 1 — para eso se escribió). Rejilla, marcas
  y ejes se derivan del color de texto con **distinta opacidad** (0.22 / 0.6 / 1), así la
  jerarquía se mantiene en los dos temas sin elegir seis colores a mano. La curva usa el
  acento: f(x) es la protagonista, mismo principio que el director fijó para la telaraña.
  Las pastillas de las etiquetas pasan a ser del color del FONDO, y el anillo del disco de
  raíz también (antes era blanco fijo, que en tema claro desaparecía).
- **Un solo color queda fijo:** el rojo de las raíces (`#e0555a`), igual que el de la órbita
  que escapa en el cobweb. "Aquí está la raíz" no es una idea que cambie con el tema.
- Borde del contenedor, texto de ayuda y botones pasan a `var(--border)` / `var(--text)` /
  `var(--bg)`, que ya siguen al tema solos.
- Repintado al cambiar de tema con `matchMedia` + `focus` + `visibilitychange`, el mismo
  patrón —y por la misma razón— que `CobwebGraph`.

**Cómo se midió G1 sin depender del color** (el método anterior buscaba los píxeles `#a78bfa`,
que ya no existen). Ahora se clasifica **pinta / no pinta** contra el fondo del tema y se
descartan las filas y columnas cubiertas de lado a lado, que son la rejilla y los ejes; lo que
queda es el trazo. Con eso, **el encuadre es idéntico en los dos temas**:

| Ecuación | Oscuro | Claro | Máscara de píxeles pintados |
|---|---|---|---|
| `sin(x)-0.5` | 78 % × 100 % | 78 % × 100 % | **99.77 %** coincidente |
| `tan(x)-x` | 83 % × 100 % | 83 % × 100 % | **99.39 %** |
| `x³−2x−5` | 78 % × 100 % | 78 % × 100 % | **99.97 %** |

La comparación de máscaras es la prueba fuerte: **las mismas posiciones se pintan en los dos
temas**, y lo que difiere (0.03–0.6 %) es el antialiasing de bordes y pastillas. Fondo del
lienzo: `rgb(22,23,29)` en oscuro y `rgb(255,255,255)` en claro — **ya no es una caja oscura
sobre página blanca**.

**Salvedad honesta sobre los números:** la métrica posicional da 78 % donde la de color daba
77 %, porque cuenta también marcas de eje y pastillas cercanas al trazo. **No es la misma
métrica y no debe compararse con el baseline histórico**; para eso está la medición del paso
2a, hecha con la métrica original ANTES de tocar la paleta. Ésta sirve para lo que sí prueba:
que el tema no mueve nada.

Consola 0 errores (con búfer limpio; los `Failed to reload` que aparecieron eran entradas
viejas del momento de editar el archivo — **tercera vez que pasa**, ver la nota de método del
paso 1). ESLint 0 errores, `npm run build` OK.

**Paso 4 — las fórmulas de Excel, como dato (2026-07-28). Primer cambio de backend de la fase.**
- `backend/excel/formula_specs.py` (NUEVO) — la especificación de Newton y Bisección: por
  columna, su cabecera, su fórmula en función de la fila, una **explicación en prosa para el
  alumno**, y qué pasa en k=0 (literal o vacía). `excel_templates.py` **no se toca**.
- `backend/test/test_formula_specs.py` (NUEVO) — **10 tests**, y es el **primer test que toca
  `excel_templates.py`** en la historia del proyecto (H3). Construye la hoja de verdad con la
  plantilla real, en memoria, y compara celda a celda tras **desenvolver el `_freeze`**.
  Si alguien cambia la plantilla, esto se rompe: es lo que evita que la copia diverja.
- `backend/main.py` (MODIFICADO, +33/−0) — `POST /practicar/plantilla`. **Aditivo**: no toca
  ningún método ni ninguna plantilla.
- **El caso de Bisección se verifica explícitamente, no por simetría con Newton** (lo pidió el
  director y lo había destapado el sondeo D2): en k=0 las columnas `a` y `b` son **literales**
  del intervalo y `Error %`/`Convergencia` están **vacías**; las fórmulas que deciden con qué
  mitad se sigue (`IF(E2*F2<0,B2,C2)`) **sólo aparecen desde k=1 y ya envueltas**. Hay dos
  tests dedicados a eso, aparte del paramétrico.
- **`spec_serializable` usa la fila 3 (k=1) por defecto**, no la 2: es la primera fila donde
  TODAS las columnas son fórmulas. En k=0 varias son literales, y en Bisección eso incluye
  justo las dos más interesantes.
- **Verificación: 162/162** en la suite completa (152 previos + 10 nuevos), y el endpoint
  ejercitado directamente: Newton y Bisección devuelven las 7 y 10 columnas correctas,
  método no cubierto → error legible, ecuación inválida → error del parser, `fila: "abc"` →
  cae a 3, y la respuesta serializa a JSON (1564 bytes).

**Paso 5 — la hoja simulada (2026-07-28).**
- `src/lib/hoja.js` (NUEVO) — `resolverHoja`, `formulaCanonica`, `celdasAEscribir` y
  `validarCelda`. **Resuelve por pasadas hasta que ningún valor cambia, no en orden fijo**,
  porque las columnas no son evaluables de izquierda a derecha: en Bisección `C` (el punto
  medio) depende de `D` (el extremo derecho), que va después en el alfabeto. Ordenar las
  dependencias a mano por método es lo que se rompe al añadir el tercero.
- `src/components/HojaCalculo.jsx` + `src/practicar.css` (NUEVOS). El alumno escribe la fila
  de régimen (k=1); las filas siguientes se ocultan hasta completarla —ver la tabla resuelta
  antes de escribir le quita la gracia—, y hay un "Ver la solución" para quien se atasque.
  Respeta D4: el `_freeze` **no aparece por ninguna parte**.
- `backend/excel/formula_specs.py` + `main.py`: `spec_hoja` y el parámetro `filas`, para servir
  la hoja entera fila a fila con el tipo de cada celda (`indice` / `inicial` / `formula` /
  `vacia`). La distinción no es cosmética: en Bisección las columnas del intervalo son
  literales en k=0 y fórmulas desde k=1.

**HALLAZGO — D3 tenía un agujero, y lo destapó la verificación.**
La decisión D3 fue "validar por valor numérico". Medido con datos reales:
```
canónica  =IF(I3<0.00001,"SI","NO")      → "NO"
alumno    =IF(I3<0.1,"SI","NO")          → "NO"     ← ¡mismo valor!
```
Un **umbral mal escrito pasaba por correcto**, porque en esa fila concreta las dos fórmulas
coinciden. Comparar en un solo punto no distingue "equivalente" de "acierta por casualidad".
**Arreglo, sin abandonar D3:** `validarCelda` compara por valor **en varios escenarios**,
sacudiendo los valores de las celdas referenciadas por factores de órdenes muy distintos
(0.5, 2, 1e-3, 1e-6, 1e3, −1, 0.05). El caso de arriba lo caza el factor 1e-3, que lleva a I3
a un valor **entre los dos umbrales**. Las formas equivalentes (`B3-C3/D3` vs `B3-(C3/D3)`)
siguen dándose por buenas: sigue siendo corrección por valor, sólo que con más de un dato.
Se añadió el veredicto `coincide-por-casualidad`, con su mensaje propio para el alumno.

- **Verificación: 35/35** casos (`smoke6`), sobre **hojas reales exportadas del backend**, no
  inventadas: Newton converge a 2.0945514815 con `G7 = "SI"`; Bisección encoge el intervalo a
  [2.0938, 2.1094] encerrando la raíz; `I2`/`J2` vacías en k=0; `C3` se resuelve pese a
  depender de `D3`; y la corrección acepta equivalentes y rechaza signo cambiado, división
  invertida, fila equivocada y sintaxis rota. Suite backend **162/162**. ESLint 0 errores,
  build OK.
- **Pendiente de verificación en navegador:** el componente todavía no está montado en ninguna
  página, así que lo comprobado es su lógica, no su pintado. Se verifica al integrarlo (paso 6).

**Paso 6 — ejercicios curados e integración de Practicar (2026-07-28). FASE 3 en pie.**
- `src/content/ejercicios.js` (NUEVO) — 4 ejercicios fijos (D1), mismo patrón que
  `gxPresets.js`: dos de Newton y dos de Bisección, con su enunciado. **Las fórmulas
  correctas NO están aquí** — las sirve el backend; duplicarlas habría creado la segunda
  fuente de verdad que `test_formula_specs.py` existe para evitar.
- `src/pages/metodos/PracticarPage.jsx` (MODIFICADO, +75/−26) — el esqueleto de FASE 1 pasa a
  selector de ejercicios + hoja. **`cargando` se DERIVA** de a qué ejercicio pertenece la
  respuesta, en vez de guardarse: así no hay `setState` síncrono en el efecto (React 19 lo
  marca como error) y, de regalo, una respuesta que llega tarde no puede pintarse sobre otro
  ejercicio — el mismo "último gana" de G8.

**SEGUNDO HALLAZGO sobre D3, y más grave que el primero → registrado como H4 en §7,
con el peso que le corresponde.** Ya en el navegador, se escribió el
criterio del intervalo **al revés** —`IF(E2*F2<0,B2,D2)` en vez de `...,B2,C2)`— y el sistema
respondió **"Correcta."**. Causa: con los datos reales `E2*F2 < 0` es cierto, así que **sólo se
evalúa la rama verdadera** y la falsa nunca se compara. Y los escenarios de `validarCelda`
multiplicaban **todas** las celdas por el mismo factor, con lo que el producto jamás cambiaba
de signo — ni con −1, porque (−E)(−F) sigue siendo negativo.
**Arreglo:** cada celda se sacude por SEPARADO, con un factor distinto por celda y por
escenario. Ahora el producto cambia de signo, la condición se invierte y la rama falsa queda
expuesta. **Al arreglarlo se rompió el caso anterior** (el del umbral): el reparto con paso 3
saltaba los factores pequeños cuando la fórmula referencia una sola celda. Reparto corregido a
`(escenario + j·4) mod n`, con un escenario por factor. **Los dos casos pasan a la vez.**

- **Verificación: 40/40** en `smoke6` y **en navegador contra el backend local**, en claro y
  oscuro: Newton carga con 6 huecos y al completarlos la hoja se despliega de 2 a 7 filas con
  `Convergencia = "SI"`; el criterio invertido se marca en rojo con el mensaje *"Da el
  resultado correcto en esta fila, pero no es la misma fórmula"*; la forma equivalente
  `B3-C3/D3` se acepta; cambiar de ejercicio recarga y resetea (0 de 9). Contraste texto/fondo
  16.25 en oscuro y 20.15 en claro. Consola 0 errores (pestaña nueva). Suite backend 162/162.
- **Cómo se verificó, porque importa:** el endpoint es nuevo y **Render no lo tiene**, así que
  se levantó el backend local y se repuntó `api.js` a `127.0.0.1:8000` **sólo durante la
  prueba**; `api.js` quedó restaurado a Render y NO entra en el commit.

⚠️ **AVISO PARA EL PUSH:** subir esto sin desplegar el backend deja la pestaña Practicar
pidiendo `/practicar/plantilla` a un Render que devuelve 404. El frontend lo enseña como
"No se pudo contactar con el servidor", que es honesto pero inútil. **El backend debe
desplegarse antes o a la vez que el frontend.**

**Regresión completa de toda la app (2026-07-28). Primera vez que TODO el código nuevo
convive en el mismo build.** Pedida por el director antes de considerar el push.

| Caso | Resultado |
|---|---|
| **G1** encuadre (métrica posicional) | `sin(x)-0.5` 78 %×100 % · `tan(x)-x` 100 %×100 % · cúbica 77 %×100 % |
| **G3** cambiar ecuación limpia resultados | ✅ y no resucitan al navegar |
| **G4** banner de cold-start pegado | ✅ **CERRADO POR FIN** (ver abajo) |
| **G8** último gana | ✅ **cerrado de verdad** (ver abajo) |
| **G11** punto fijo desde la g dibujada | ✅ \|g′\|=0.2899 en el punto fijo real; sin marcador si escapa |
| **G12** menos Unicode U+2212 | ✅ "Interpretado como x**2 -2" |
| **G13** x₀ ya es el punto fijo | ✅ mensaje propio, no "converge" |
| **Practicar A–E** | ✅ correcta · equivalente · signo invertido · umbral malo · vacío |
| **H4** criterio del intervalo invertido | ✅ sigue cazándose |
| Estado del módulo | ✅ ecuación y resultado sobreviven al navegar |
| Temas | ✅ lienzos de Calcular y Aprender en `rgb(22,23,29)` en oscuro |

**G4 y G8, cerrados con un backend falso y LENTO.** Llevaban dos bloques sin poder
verificarse porque su síntoma exige que Render tarde. Se midió que Render **estaba dormido**
(22.5 s en responder)… y esa misma medición lo despertó, consumiendo la ocasión. Solución:
un servidor de 40 líneas que sólo tarda (`scratchpad/lento.mjs`, 14 s de retraso) al que se
apunta `api.js` durante la prueba. Con él:
- **G4:** sin banner al inicio → "Calculando" a 1.5 s → **banner a 5.5 s** → al cambiar la
  ecuación **desaparece**, y sigue sin volver 2 s después. De paso confirma **G9** (el banner
  se anuncia a los ~4.5 s, no al primer fallo).
- **G8:** consulta lanzada, abandonada al cambiar de ecuación, y **la respuesta tardía que
  llega 14 s después NO se pinta**.
Queda como técnica reutilizable: **para verificar comportamiento que depende de latencia, no
se espera a que el entorno colabore — se falsifica la latencia.**

**El panel de ayuda de la hoja: era artefacto de prueba, no bug.** Quedaba a medias. Cadena de
evidencia: `document.hasFocus()` es **false** —el panel del navegador nunca tiene el foco del
sistema— y en esa condición `.focus()` asigna `activeElement` pero **no dispara ningún
evento**: se registró un listener DOM propio, sin React de por medio, y recibió **cero**
`focus` y **cero** `focusin`. El componente está bien: en cuanto llega un `focusin`, el panel
abre. **Limitación:** no se pudo producir un foco real del sistema (el clic vía CDP exige
captura previa, y la captura falla porque el panel no se muestra), así que la conclusión se
apoya en que el evento no llega, no en haber visto el caso real funcionar.
**Es la tercera vez que una prueba de interacción da un falso negativo por cómo se sintetiza
el evento** (antes: `mouseleave` en la telaraña, y el búfer viejo de consola). Regla práctica:
antes de declarar un bug de interacción, comprobar que el evento **llegó a dispararse**.

**Frontend — SIN integrar (decisión explícita, dejado para después):**
- ~~Canvas del gráfico adaptable claro/oscuro~~ — ✅ **HECHO en FASE 3, paso 2b** (2026-07-28).
- Aviso de "raíz exacta" (cuando x₀ ya es la raíz, iters=0).
- Barra de símbolos rápidos (π, √, x², ÷, ×) — el normalizador ya cubre la notación,
  faltan los botones.

---

## 6. Reglas de trabajo (IMPORTANTE)

1. **Verificar contra el código real antes de afirmar que algo es un bug.** En la asesoría,
   dos "bugs" supuestos (x=1, fallo de auto_params) resultaron falsos al ejecutar.
2. **No instalar MathQuill/MathLive.** Se usa el normalizador ligero `mathNotation.js`.
3. **No tocar el motor matemático sin tests.** Mantener 152/152.
4. **`npm run build` antes de entregar cambios de frontend.**
5. **Cold start de Render:** todo fetch nuevo contempla retry + aviso al usuario.
6. **`amburger.xlsx` = fuente de verdad** para formato y fórmulas de Excel.
7. **No reemplazar archivos a ciegas:** mostrar diff y esperar confirmación.
8. **Comprobar caracteres de alfabetos ajenos antes de commitear documentación.** Se han
   colado tres veces —un ideograma CJK (U+63A7) y dos cirílicas dentro de la palabra "genera"
   (U+0433, U+0435)— en textos por lo demás en español; a simple vista no se distinguen.
   Se ejecuta a mano: `python scripts/check_chars.py` (o pasándole un archivo o carpeta).
   **No los caza ningún linter:** para ESLint y para pytest son texto dentro de un comentario
   o de una cadena. El chequeo marca cirílico, CJK, hangul, kana, árabe, hebreo y devanagari, y
   **no** prohíbe lo no-ASCII: tildes, ñ, π, √, ², ₊, ≈, ─ y → son del proyecto y pasan.
   **De invocación manual a propósito** (decisión del director, 2026-07-28): no es un hook de
   pre-commit y no bloquea commits; está para correrlo cuando se pida.
   Una línea que contenga el marcador `chars-ok` se salta, para poder citar un glifo a
   propósito — sin esa vía de escape, esta misma regla se marcaría a sí misma.
9. **Este CLAUDE.md se actualiza ANTES de commitear el código.** Al terminar
   cualquier tarea (bug, feature o decisión) se anota aquí qué se hizo, el commit y
   el estado nuevo, en la misma tarea — no como paso posterior.
   **Si algo no está en el CLAUDE.md, no existe.** (Regla permanente del director,
   2026-07-21. Motivo: G8 y G9 quedaron solo en mensajes de commit y el estado real
   se desincronizó del documentado.) Cuando lo que cambia es el plan o la fase —no el
   estado técnico— el documento a actualizar es `VISION_PLATAFORMA.md`.

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
    **Desde FASE 1 este `useEffect` vive en `PlataformaLayout`, no en la calculadora** (ver §5).
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
6. ✅ HECHO — Estructura de navegación (react-router v7), FASE 1, 2026-07-22
   (commits `6e9eeb4` + `267b349`). Vestíbulo + pestañas Aprender/Practicar/Calcular.
   Detalle en §5.
7. Identidad académica: landing, encabezado institucional. **`<title>` ✅ hecho en FASE 1**
   (ahora "NumériCa — Plataforma de matemática computacional", `lang="es"` + meta
   description). Quedan pendientes la landing y el encabezado institucional.
8. **Constructor de Excel paso a paso** — el diferenciador único del proyecto.
9. Corregir Newton 2do orden (ambas ramas del discriminante).
10. Reconciliar Ostrowsky con la fórmula estándar de 2 pasos (hoy usa la variante `copysign`,
    que funciona; reconciliación diferida — acordado con el director).
11. Modo práctica / examen.
12. ✅ HECHO — Push de los 5 commits a `origin/main` (2026-06-14). Vercel desplegó el build
    nuevo; backend de Render compatible y verificado en vivo. (PR no aplica: trabajo directo en `main`.)

**Fuera de alcance explícito:** hoja Resumen (C4).

**Hallazgos con entrada propia (NO son deuda técnica). Los abiertos esperan decisión de fase;
los cerrados quedan aquí por su gravedad, para que nadie los reintroduzca sin saberlo.**

- **H5 — CERRADO: Practicar se quedaba EN BLANCO Y EN SILENCIO contra el backend desplegado,
  y yo había afirmado lo contrario.** Descubierto en la regresión completa, apuntando a Render.
  **Qué pasaba:** `/practicar/plantilla` no existe en el backend desplegado, así que Render
  devuelve `404 {"detail":"Not Found"}`. Un 404 **no hace fallar al `fetch`**, de modo que el
  `catch` de red nunca entraba; el cuerpo se parseaba bien, `json.error` no existía y el código
  lo trataba como **respuesta buena**. Resultado: `hoja` quedaba `undefined` y la página
  mostraba la introducción y los botones… y **nada más**. Ni tabla, ni error, ni "cargando".
  **La corrección importa doble** porque en el aviso de despliegue del paso 6 yo escribí que
  el frontend lo enseñaría como *"No se pudo contactar con el servidor"*. **Era falso**: no
  enseñaba nada. Un fallo silencioso es peor que uno ruidoso, y lo peor es un aviso que
  describe un comportamiento que no ocurre.
  **Arreglo:** comprobar `r.ok` antes de tratar el cuerpo como bueno, con mensaje específico
  para el 404 que nombra el endpoint que falta. Verificado contra Render: ahora dice *"El
  servidor respondió 404: el backend desplegado todavía no tiene el endpoint
  /practicar/plantilla"*.
  **Lección:** `fetch` sólo rechaza por fallo de red. Todo código que lo use tiene que mirar
  `r.ok`; comprobar únicamente el campo de error propio deja pasar todos los errores HTTP.
  (Conviene revisar si el resto de llamadas del proyecto tienen el mismo hueco — **no
  revisado todavía**, ver deuda técnica.)

- **H4 — CERRADO, pero es el hallazgo más grave de FASE 3: el validador aprobaba una fórmula
  INCORRECTA.** Riesgo de credibilidad académica del mismo orden que H1: un corrector que da
  falsos positivos **enseña el método mal**, y el alumno no tiene forma de saberlo. Es peor
  que no tener corrector.
  **Qué pasaba.** Con el criterio del intervalo de Bisección escrito al revés
  —`IF(E2*F2<0,B2,D2)` en lugar de `...,B2,C2)`— el sistema respondía **"Correcta."**
  **Por qué.** Con los datos reales `E2*F2 < 0` es cierto, así que **sólo se evalúa la rama
  verdadera y la falsa nunca llega a compararse**. La corrección por valor (D3) no ve la
  diferencia porque en esa fila no la hay.
  **Y por qué no lo cazó el primer arreglo.** Los escenarios de `validarCelda` multiplicaban
  **todas** las celdas por el mismo factor, y eso **nunca cambia el signo de un producto**:
  (−E)(−F) sigue siendo negativo. El generador de escenarios tenía el mismo defecto de fondo
  que el bug que buscaba — álgebra elemental que se escapó en el primer intento, y que las
  pruebas sintéticas no destaparon porque estaban escritas con la misma idea equivocada.
  **Cómo se encontró (y esto es lo que hay que repetir):** NO por la batería, que estaba en
  verde, sino **tecleando el error a mano en el navegador**. Una batería sintética sólo
  comprueba lo que a uno se le ocurrió comprobar.
  **Arreglo:** cada celda se sacude por SEPARADO, con un factor distinto por celda y por
  escenario, de modo que el producto cambia de signo, la condición se invierte y la rama falsa
  queda expuesta. **Al arreglarlo se rompió el caso anterior** (el umbral mal escrito): el
  reparto saltaba los factores pequeños con fórmulas de una sola referencia. Reparto corregido
  a `(escenario + j·4) mod n`, un escenario por factor. Los dos casos pasan a la vez.
  **Lección permanente:** para un corrector, "pasa las pruebas" no es evidencia suficiente.
  Hay que intentar **engañarlo a mano** con los errores que un alumno cometería de verdad —
  sobre todo en fórmulas con ramas (`IF`), donde los datos de una fila concreta pueden no
  ejercitar la rama equivocada. Antes de dar por bueno el validador de un método nuevo,
  escribir a propósito: signo cambiado, división invertida, referencias intercambiadas,
  umbral alterado.
  **Cobertura actual:** 9 escenarios de sacudida (aprobado por el director el 2026-07-28,
  "mejor pecar de más verificación que menos"). Si algún día el ritmo al teclear molesta, se
  ajusta **con datos reales de uso, no antes**.



- **H1 — El "Punto Fijo" automático es Newton disfrazado.** Medido el 2026-07-27 contra el
  backend local, al verificar la premisa de D3:
  ```
  g(x) automática de x³−2x−5  =  (2x³+5)/(3x²−2)      ← es exactamente x − f/f′
  Punto Fijo → 3 iteraciones, raíz 2.0945514815423265
  Newton     → 3 iteraciones, raíz 2.0945514815423265   (idéntica hasta el último dígito)
  ```
  **Causa:** `_generate_gx_candidates` ([auto_params.py:124]) sólo implementa la estrategia
  S1 = `x − f(x)/f'(x)`, y `generate_params` toma el mejor candidato → siempre esa.
  **Consecuencias:** (a) el alumno elige "Punto Fijo" y recibe la iteración de Newton;
  (b) el criterio |g′| < 1, que es TODA la enseñanza del método, nunca se pone a prueba,
  porque |g′(r)| = 0 por construcción; (c) el cobweb con la g automática converge de golpe,
  sin escalera ni espiral — el menos ilustrativo posible. Medido en punto_fijo; **por
  construcción afecta también a Aitken y Steffensen**, los otros dos que consumen `gx`
  (según la nota de G6), aunque eso NO se ha medido todavía.
  **No es un error de cálculo:** es un punto fijo legítimo y la raíz que da es correcta.
  **Estado: no tocado, sin fase asignada** (decisión del director, 2026-07-27: registrarlo
  aparte para poder decidir su fase por separado, no diluido entre los pendientes).
  **Para decidir hace falta** contrastar contra `amburger.xlsx` qué g(x) usa su hoja de
  Punto Fijo: si usa un reordenamiento clásico, esto es una desviación de la fuente de
  verdad (regla 6.6) y pasa a ser bug; si no, es comportamiento aceptado y se documenta.
  **Reproducir:** `generate_params(parse_equation('x**3 - 2*x - 5')).gx_sympy` desde la raíz
  del repo. Tocarlo implica motor matemático + plantillas de Excel + los 152 tests.

- **H2 — PATRÓN: cuatro veces el documento ha prometido lo que el código no tiene.**
  No son anécdotas sueltas; es la razón por la que la regla 1 existe y por la que conviene
  medir antes de construir. Los cuatro casos, todos verificados ejecutando:
  1. **`gx_candidates`** (FASE 2, D3): su docstring anuncia varias estrategias de g(x);
     sólo está implementada la S1. Nunca hay más de un candidato. → D3 revertida.
  2. **`formulas`** (FASE 3): figura en §8 como dependencia de entorno, pero **ningún
     archivo del repo la importa**. No hay evaluador de fórmulas de Excel en el proyecto,
     en ningún lenguaje. → `lib/celdas.js` se escribió de cero.
  3. **La premisa de D4** (FASE 1→3): la deuda de estado se anotó diciendo que Aprender
     compartiría su ecuación. `AprenderPage` **nunca tuvo ecuación** —su único estado es el
     método— y la telaraña usa presets. → el objetivo del refactor tuvo que replantearse.
  4. **La cobertura de los 152 tests** (FASE 3): ver H3.
  **Qué hacer con esto:** antes de construir sobre una afirmación de este documento, de un
  docstring o de un plan aprobado, ejecutar el código y comprobarla. Las cuatro veces el
  coste de verificar fue de minutos; construir encima habría costado días.

- **H3 — Hueco de cobertura real: `excel_templates.py` no tiene NINGÚN test.**
  Medido en FASE 3: el único import de Excel en toda la suite es
  `from backend.excel.excel_generator import _has_real_roots` (en `test_real_roots_detection.py`).
  **`backend/excel/excel_templates.py` —1091 líneas, donde vive cada fórmula de cada método—
  importa cero veces.** Los "152/152 tests pasando" cubren métodos y parseo, **no** el Excel.
  **Consecuencia para quien lo toque:** un cambio ahí no lo atrapa la suite; el fallo sólo
  aparecería al abrir un .xlsx descargado. Si hay que modificarlo, hay que traer los tests.
  (Por eso FASE 3 decidió NO tocarlo y exponer las fórmulas desde un módulo aparte fijado
  por un test de coincidencia — ver §5.)

**Deuda técnica:**
- **¿Miran `r.ok` las demás llamadas del proyecto? — SIN REVISAR.** H5 destapó que comprobar
  sólo el campo de error propio deja pasar cualquier error HTTP. `fetchWithWake` y las
  llamadas de `CalcularPage` (`/params`, `/method/*`, `/excel/*`) **no se han auditado** con
  ese criterio. Es revisión, no rediseño; conviene hacerla antes de añadir más endpoints.
- ✅ **RESUELTO (2026-07-28): el chequeo de caracteres vive en `scripts/check_chars.py`.**
  Decisión del director: **script invocable a mano, no hook de pre-commit** — que esté
  disponible, no que bloquee commits. Estrena la carpeta `scripts/`.
  La limitación que tenía (marcarse a sí mismo al citar un glifo como ejemplo) se resolvió con
  un marcador de excepción por línea, así que la regla 6.8 ya puede nombrarlos como quiera.
  **Verificado con un control negativo, no sólo con el caso limpio:** sobre un archivo con las
  dos cirílicas de "genera" y un ideograma CJK, los caza los tres, los nombra
  (`CYRILLIC SMALL LETTER GHE`…), salta la línea marcada y sale con código 1.
- Optimización futura: cargar KaTeX de forma diferida (lazy load) para recuperar el
  peso inicial del bundle (~260 kB extra). No urgente.
- ✅ **SALDADA en FASE 3, paso 1** (2026-07-28) — ver §5. Lo que sigue queda como registro de
  la deuda y de por qué su premisa original era falsa (H2, caso 3).
- **Estado no compartido entre pestañas (deuda de FASE 1 → resolver en FASE 3).**
  Al navegar de Calcular a Aprender/Practicar, `CalcularPage` se desmonta y pierde todo
  su estado (ecuación, parámetros, resultados, tabla); al volver, arranca en blanco con
  `x^3 - 2*x - 5`. **Aceptado a propósito en Fase 1** (decisión del director): Aprender y
  Practicar están vacías, no hay trabajo del estudiante que perder, y subir el estado es
  refactor que no cabe en la misma fase que la navegación. **Deja de ser aceptable en
  FASE 3**, donde `VISION_PLATAFORMA.md` §3 dice que Practicar reutiliza el gráfico y las
  derivadas de Aprender. Arreglo previsto: subir `equation` (y lo que se comparta) a
  `ModuloLayout` como estado del módulo, o a un contexto.
- **Migración de `CalcularPage` a `lib/evalExpr.js` y `components/Katex.jsx` (FASE 2, paso 1).**
  `CalcularPage` conserva su `evalF` y su `Katex` privados; los módulos nuevos son hermanos,
  no reemplazos. **Decisión del director (D2):** ese archivo carga 9 bugs cerrados y
  verificados en vivo (G1–G9) y migrarlo no aporta nada a la telaraña. Hacerlo **aislado**,
  con su propia batería de regresión (G1: `sin(x)-0.5` encuadra al 77% del alto; G3: cambiar
  ecuación limpia resultados), cuando no compita con una feature nueva. Mientras tanto
  conviven dos evaluadores y dos `Katex` de 9 líneas. **Ojo: `evalExpr` NO es idéntico a
  `evalF`** — entiende `Abs`/`cbrt` y protege la notación científica, cosas que `evalF` no
  hace; la migración es una mejora de comportamiento, no un movimiento literal, y por eso
  necesita su propia verificación.
- **Mejoras de la telaraña aplazadas a FASE 4 (candidatos, NO construir antes).** Registradas
  por decisión del director el 2026-07-27, con la telaraña ya funcionando:
  - **Zoom y desplazamiento interactivos en el cobweb.** Hoy el encuadre es automático y no se
    puede acercar. **Requisito no negociable si se implementa: el zoom debe escalar X e Y
    JUNTOS.** La telaraña vive de que la recta y = x se vea a 45°; un zoom por eje —como el que
    usa `FunctionGraph`, donde es correcto (G1)— rompería el ángulo y con él toda la intuición
    del rebote. En la práctica significa multiplicar el `scale` único de `isoView` y recentrar,
    nunca tocar `scaleX` y `scaleY` por separado.
  - **Refuerzo de color por recencia del trazo.** Los últimos segmentos de la órbita se
    dibujarían más intensos y los primeros más apagados, para que se lea de un vistazo hacia
    dónde avanza la iteración sin tener que usar el paso a paso. Encaja con la paleta de
    `plotCore.js` (misma familia de color, distinta opacidad).
  - Ambas son mejoras de la visualización que ya existe, no piezas nuevas: por eso van a
    FASE 4 (*"otras visualizaciones… más métodos"*, `VISION_PLATAFORMA.md` §4) y no a FASE 3,
    que es Practicar.
- **Candidato a G10 (no abordado) — posible carrera en `fetchAutoParams`:** al tipear
  rápido en la ecuación, `fetchAutoParams` (`pages/metodos/CalcularPage.jsx`, ex-App.jsx)
  dispara un `fetch` a `/params`
  por cada cambio sin guarda de "último gana", así que la respuesta de una ecuación
  vieja podría pisar `autoParams`/`graphRoots` de la nueva (params/raíces rancios).
  Queda **fuera del alcance de G8** (que cubre solo el flujo de cálculo de `resolver`/
  `resolverTodos`); es un flujo aparte y menor (los params son editables y las raíces
  son del gráfico). **Revisar solo si algún día se ven params/raíces rancios al
  escribir;** el arreglo sería extender el mismo patrón `reqIdRef` a `fetchAutoParams`.

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
