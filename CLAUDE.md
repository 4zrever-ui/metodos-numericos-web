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

**Limitación de la verificación (importante):** **no hay capturas de pantalla** de ninguna
parte de FASE 2. El panel del navegador debe estar visible para que la página componga frames
y no lo estaba, así que todo lo anterior es **medición del DOM y de los píxeles del canvas**,
no inspección visual. Queda comprobado *qué* se dibuja y *dónde*; el juicio estético (grosor
del trazo, ritmo de la animación, si el punto fijo se pierde sobre la rejilla) es del director.

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
3. **No tocar el motor matemático sin tests.** Mantener 152/152.
4. **`npm run build` antes de entregar cambios de frontend.**
5. **Cold start de Render:** todo fetch nuevo contempla retry + aviso al usuario.
6. **`amburger.xlsx` = fuente de verdad** para formato y fórmulas de Excel.
7. **No reemplazar archivos a ciegas:** mostrar diff y esperar confirmación.
8. **Este CLAUDE.md se actualiza ANTES de commitear el código.** Al terminar
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

**Hallazgos abiertos (con entrada propia, fase por decidir — NO son deuda técnica):**

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

**Deuda técnica:**
- Optimización futura: cargar KaTeX de forma diferida (lazy load) para recuperar el
  peso inicial del bundle (~260 kB extra). No urgente.
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
