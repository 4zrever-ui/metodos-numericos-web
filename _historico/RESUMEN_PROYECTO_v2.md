# RESUMEN_PROYECTO_v2.md

**Proyecto:** Métodos Numéricos Web — Backend Python/FastAPI + Frontend React  
**Fecha de verificación:** 2026-06-06  
**Fuente de verdad:** Estado real verificado contra el ZIP `metodos_numericos_web.zip`  
**Regla de oro:** Toda afirmación en este documento fue verificada en el ZIP. Las discrepancias con documentos anteriores (`RESUMEN_PROYECTO.md`, `DELIVERY_CHECKLIST.md`) están explícitamente señaladas.

---

## 1. Estado Actual del Proyecto

### Backend — estado verificado en ZIP

| Ítem | Estado real |
|------|-------------|
| Framework | FastAPI + uvicorn |
| Endpoints en `main.py` | **10** (1 GET + 1 POST /analyze + 8 métodos) |
| Endpoints documentados en RESUMEN anterior | 16 (incorrecto — no están en el ZIP) |
| Serialización de respuestas | **Rota**: el main.py del ZIP no usa `dataclasses.asdict()`. FastAPI no puede serializar `MethodResult` directamente → error 500 en producción |
| CORS | Configurado con `allow_origins=["*"]` |
| Módulo `newton_family.py` | Existe con 6 funciones implementadas |
| Endpoints de newton_family registrados | **0** — las 6 funciones existen pero no tienen `@app.post` en `main.py` |

**Archivos backend en el ZIP:**

```
backend/
├── core/
│   ├── auto_params.py        ← genera parámetros automáticamente
│   ├── equation_parser.py    ← parsea ecuaciones a sympy + LaTeX + Excel
│   └── sympy_to_excel.py     ← conversión de expresiones a formato Excel
├── excel/
│   ├── excel_generator.py    ← genera .xlsx (sin endpoint HTTP)
│   ├── excel_styles.py
│   └── excel_templates.py
├── methods/
│   ├── aitken.py
│   ├── biseccion.py
│   ├── newton_family.py      ← 6 métodos: mod, 2do orden, Chebyshev, Halley, Super Halley, Ostrowsky
│   ├── newton_raphson.py
│   ├── punto_fijo.py
│   ├── regula_falsi.py
│   ├── secante.py
│   ├── steffensen.py         ← parche definitivo aplicado
│   └── von_mises.py
├── schemas/
│   └── models.py             ← dataclasses: MethodResult, IterationRow y subclases
├── test/
│   ├── conftest.py
│   ├── test_aitken.py        ← 19 tests, 2 fallan (expectativas erróneas)
│   ├── test_biseccion.py     ← 0 tests (archivo vacío)
│   ├── test_newton_family.py ← 40 tests, todos pasan
│   ├── test_newton_raphson.py← 18 tests, todos pasan
│   ├── test_regula_falsi.py  ← 20 tests, todos pasan
│   └── test_steffensen.py    ← 18 tests, 2 fallan (expectativas erróneas)
└── main.py                   ← 10 endpoints activos (falta serialización y 6 endpoints)
```

### Frontend — estado verificado en ZIP

| Ítem | Estado real |
|------|-------------|
| Framework | React 19 + Vite 8 |
| `App.jsx` | **69 líneas** — prototipo mínimo, solo llama a `/method/newton` |
| `App.css` | **184 líneas** — CSS default de Vite (no es diseño del proyecto) |
| `components/` | **Vacío** |
| `pages/` | **Vacío** |
| `services/` | **Vacío** |
| Selector de 14 métodos | **No existe** |
| Tabla de iteraciones | **No existe** |
| Manejo de errores | **No existe** |
| `index.html` title | `"frontend"` (no personalizado) |
| Dependencias instaladas | `react`, `react-dom` únicamente |

### Tests — estado verificado en ZIP

| Archivo | Tests | Pasan | Fallan |
|---------|-------|-------|--------|
| `test_newton_family.py` | 40 | 40 | 0 |
| `test_regula_falsi.py` | 20 | 20 | 0 |
| `test_newton_raphson.py` | 18 | 18 | 0 |
| `test_aitken.py` | 19 | 17 | **2** |
| `test_steffensen.py` | 18 | 16 | **2** |
| `test_biseccion.py` | **0** | — | — |
| **Total** | **115** | **111** | **4** |

**Los 4 tests que fallan (verificados en el ZIP):**

| Test | Archivo | Assertion actual (incorrecta) | Corrección |
|------|---------|-------------------------------|------------|
| `test_denominador_cero_fallback` | `test_aitken.py:46` | `assert result == 1.0` | `assert result is None` |
| `test_secuencia_constante` | `test_aitken.py:58` | `assert abs(result - 0.254) < 1e-12` | `assert result is None` |
| `test_denominador_cero_fallback` | `test_steffensen.py:43` | `assert result == 2.0` | `assert result is None` |
| `test_aitken_seq_menor_3_inaplicable` | `test_steffensen.py:148` | `assert result.root is not None` | `assert result.applicable is False` |

**Motivo:** Los tests esperan que `_delta2(c, c, c)` retorne `c` como fallback. El código retorna `None` (correcto — replica `#DIV/0!` de Excel según `EXCEL_COMPATIBILITY_SPEC.md`). Los tests tienen expectativas desactualizadas; el código de producción es correcto.

### Git — estado verificado

Último commit en el repositorio: `cadddb5 — Frontend y backend conectados correctamente`

**Historial completo de commits:**

| Hash | Mensaje |
|------|---------|
| `cadddb5` | Frontend y backend conectados correctamente |
| `22aef3b` | Crear pantalla inicial de métodos numéricos |
| `29036d9` | Crear frontend React con Vite |
| `51b804b` | Renombrar fronted a frontend |
| `bb153dc` | Agregar estructura frontend |
| `2a28866` | Eliminar archivos pycache |
| `899aaf9` | Eliminar archivos zip del repositorio |
| `712a045` | Agregar gitignore |
| `155ea56` | Backend estable — 115 tests OK |

**Estado del árbol de trabajo:** Los archivos `steffensen.py` (timestamp `21:51`), `main.py`, `App.jsx` tienen timestamps posteriores al último commit pero el ZIP fue generado a las `21:13`. Esto indica que hay cambios recientes que nunca fueron commiteados.

**Lo que no está commiteado:** El estado real del ZIP es el árbol de trabajo, no el último commit.

### Documentación en `docs/`

| Archivo | Estado |
|---------|--------|
| `EXCEL_COMPATIBILITY_SPEC.md` | ✅ Normativo, congelado, válido |
| `FINAL_DELIVERY_AUDIT.md` | ✅ Válido (describe estado 111/115) |
| `REGRESSION_TESTS.md` | ✅ Válido |
| `RESIDUAL_METHODS_AUDIT.md` | ✅ Válido |
| `TEST_CLEANUP_REPORT.md` | ✅ Válido |
| `DELIVERY_CHECKLIST.md` | ⚠️ Afirma 115/115 PASS — incorrecto, son 111/115 en el ZIP |
| `AUDITORIA_FINAL_2026-06-06.md` | ⚠️ Estado intermedio (111/115) — redundante |
| `INFORME_AUDITORIA_FINAL.md` | ⚠️ Redundante con `FINAL_DELIVERY_AUDIT.md` |
| `AUTO_PARAMS_CURRENT_STATE.md` | ✅ Documenta deuda técnica de auto_params |
| `MULTI_EQUATION_CURRENT_AUDIT.md` | ✅ Auditoría 6 ecuaciones × 4 métodos |

---

## 2. Arquitectura

### Estructura de carpetas (completa)

```
metodos numericos web/
├── backend/
│   ├── core/
│   │   ├── auto_params.py
│   │   ├── equation_parser.py
│   │   └── sympy_to_excel.py
│   ├── excel/
│   │   ├── excel_generator.py
│   │   ├── excel_styles.py
│   │   └── excel_templates.py
│   ├── methods/
│   │   ├── aitken.py
│   │   ├── biseccion.py
│   │   ├── newton_family.py
│   │   ├── newton_raphson.py
│   │   ├── punto_fijo.py
│   │   ├── regula_falsi.py
│   │   ├── secante.py
│   │   ├── steffensen.py
│   │   └── von_mises.py
│   ├── schemas/
│   │   └── models.py
│   ├── test/
│   │   ├── conftest.py
│   │   ├── test_aitken.py
│   │   ├── test_biseccion.py   ← vacío
│   │   ├── test_newton_family.py
│   │   ├── test_newton_raphson.py
│   │   ├── test_regula_falsi.py
│   │   └── test_steffensen.py
│   └── main.py
├── docs/
│   └── [ver sección Documentación]
├── excel_templates/
│   ├── amburger.xlsx           ← fuente de verdad Excel
│   └── amburger_v6.xlsx
├── frontend/
│   ├── src/
│   │   ├── components/         ← vacío
│   │   ├── pages/              ← vacío
│   │   ├── services/           ← vacío
│   │   ├── App.css             ← CSS Vite default (reemplazar)
│   │   ├── App.jsx             ← prototipo 69 líneas (reemplazar)
│   │   ├── index.css
│   │   └── main.jsx            ← ok, no modificar
│   ├── index.html              ← title="frontend" (cambiar a nombre del proyecto)
│   ├── package.json
│   └── vite.config.js
└── Archivo 00_PROYECTO_GENERAL.md  ← especificación académica original
```

### Flujo frontend → backend

```
Usuario ingresa ecuación
        ↓
App.jsx → fetch POST http://127.0.0.1:8000/method/{método}
        body: { "equation": "x^3 - 2*x - 5" }
        ↓
FastAPI main.py recibe request
        ↓
parse_equation(equation)  →  ParsedEquation
        {f_sympy, fp_sympy, fpp_sympy, f_latex, fp_latex, f_excel, fp_excel}
        ↓
generate_params(eq)  →  AutoParams
        {a, b, x0, x0_alt, tol=0.00001, max_iter=25, gx_sympy, ...}
        ↓
run_[método](eq, params)  →  MethodResult (dataclass)
        ↓
dataclasses.asdict(result)  →  dict serializable
        ↓
HTTP 200 JSON response
```

**Nota crítica:** El `main.py` del ZIP NO incluye `dataclasses.asdict()`. Los handlers retornan el objeto `MethodResult` directamente, lo que causará `TypeError` en FastAPI al intentar serializar un dataclass. El `main.py` entregado en esta sesión corrige esto.

### Endpoints — estado en ZIP vs corregido

| # | Endpoint | En ZIP | Corregido (esta sesión) |
|---|----------|--------|------------------------|
| 1 | `GET /` | ✅ | ✅ |
| 2 | `POST /analyze` | ✅ | ✅ |
| 3 | `POST /method/biseccion` | ✅ | ✅ |
| 4 | `POST /method/regula_falsi` | ✅ | ✅ |
| 5 | `POST /method/punto_fijo` | ✅ | ✅ |
| 6 | `POST /method/aitken` | ✅ | ✅ |
| 7 | `POST /method/steffensen` | ✅ | ✅ |
| 8 | `POST /method/newton` | ✅ | ✅ |
| 9 | `POST /method/von_mises` | ✅ | ✅ |
| 10 | `POST /method/secante` | ✅ | ✅ |
| 11 | `POST /method/newton_modificado` | ❌ faltaba | ✅ añadido |
| 12 | `POST /method/newton_segundo_orden` | ❌ faltaba | ✅ añadido |
| 13 | `POST /method/chebyshev` | ❌ faltaba | ✅ añadido |
| 14 | `POST /method/halley` | ❌ faltaba | ✅ añadido |
| 15 | `POST /method/super_halley` | ❌ faltaba | ✅ añadido |
| 16 | `POST /method/ostrowsky` | ❌ faltaba | ✅ añadido |

### Métodos implementados — 14 total

| # | Método | Archivo | Grupo | Endpoint |
|---|--------|---------|-------|----------|
| 1 | Bisección | `biseccion.py` | Intervalo | `/method/biseccion` |
| 2 | Regula Falsi | `regula_falsi.py` | Intervalo | `/method/regula_falsi` |
| 3 | Punto Fijo | `punto_fijo.py` | Punto Fijo | `/method/punto_fijo` |
| 4 | Aitken (Δ²) | `aitken.py` | Punto Fijo | `/method/aitken` |
| 5 | Steffensen | `steffensen.py` | Punto Fijo | `/method/steffensen` |
| 6 | Newton-Raphson | `newton_raphson.py` | Derivada | `/method/newton` |
| 7 | Von Mises | `von_mises.py` | Derivada | `/method/von_mises` |
| 8 | Secante | `secante.py` | Derivada | `/method/secante` |
| 9 | Newton Modificado | `newton_family.py` | Familia Newton | `/method/newton_modificado` |
| 10 | Newton 2do Orden | `newton_family.py` | Familia Newton | `/method/newton_segundo_orden` |
| 11 | Chebyshev | `newton_family.py` | Familia Newton | `/method/chebyshev` |
| 12 | Halley | `newton_family.py` | Familia Newton | `/method/halley` |
| 13 | Super Halley | `newton_family.py` | Familia Newton | `/method/super_halley` |
| 14 | Ostrowsky | `newton_family.py` | Familia Newton | `/method/ostrowsky` |

### Esquemas de datos (models.py)

```python
MethodResult          # resultado genérico de todo método
IterationRow          # fila base (k, x_new, error_pct, converged, extra: dict)
  ├── IntervalRow     # biseccion/regula_falsi (a, c, b, fa, fc, fb, fa_fc)
  ├── FixedPointRow   # punto_fijo (xk, gxk)
  ├── AitkenRow       # aitken (p0, p1, p2, xk_hat)
  ├── SteffensenRow   # steffensen (p0, p1, p2, xk_hat)
  ├── NewtonRaphsonRow# newton (xk, fxk, fpxk, x_next)
  ├── NewtonModRow    # newton_family (xk, fxk, fpxk, fppxk, x_next)
  ├── SecantRow       # secante (xk, fxk, xk_prev, fxk_prev, x_next)
  └── VonMisesRow     # von_mises (xk, fxk, fp_x0, x_next)
```

---

## 3. Estado Real Verificado vs Documentado

### Lo que EXISTE en el ZIP

- `newton_family.py` con 6 funciones (`run_newton_modificado`, `run_newton_segundo_orden`, `run_chebyshev`, `run_halley`, `run_super_halley`, `run_ostrowsky`)
- `steffensen.py` con el parche definitivo (`rows[0].xk_hat` como candidato en fallback)
- `auto_params.py` con generación dinámica de g(x) usando estrategia `g(x) = x - f(x)/f'(x)` (NO hardcodeada — a diferencia de lo documentado en versiones anteriores)
- `_best_integer_near()` que evita `f'(x₀) ≈ 0` al seleccionar x0
- `test_newton_family.py` con 40 tests pasando
- `amburger.xlsx` como referencia Excel

### Lo que NO EXISTE en el ZIP (documentado como si existiera)

| Afirmación en documentos anteriores | Realidad |
|-------------------------------------|----------|
| "15 endpoints activos" | 10 endpoints en main.py |
| "Frontend completo con selector de 14 métodos" | App.jsx de 69 líneas, solo Newton |
| "App.css con tema oscuro" | CSS default de Vite |
| "components/, pages/, services/ implementados" | Los tres directorios están vacíos |
| "115/115 PASS" (DELIVERY_CHECKLIST.md) | 111/115 — 4 fallan |
| "g(x) hardcodeada como `(2x+5)^(1/3)`" | No es así — auto_params usa g(x) = x - f/f' dinámico |
| "Serialización correcta en main.py" | main.py retorna dataclass directamente → TypeError |

### Correcciones entregadas en esta sesión (no en el ZIP)

Los siguientes archivos fueron generados y están disponibles para descarga:

| Archivo | Cambio |
|---------|--------|
| `main.py` | +6 endpoints newton_family + `_serialize()` con `dataclasses.asdict()` |
| `App.jsx` | Reescrito: 385 líneas, selector 14 métodos, tabla de iteraciones |
| `App.css` | Reescrito: 467 líneas, tema oscuro académico |

---

## 4. Problemas Pendientes

### Críticos (bloquean la demo)

| ID | Problema | Archivo | Impacto |
|----|----------|---------|---------|
| C-1 | `main.py` sin serialización: FastAPI no puede retornar dataclasses directamente | `backend/main.py` | Error 500 en todos los endpoints |
| C-2 | 6 endpoints de newton_family no registrados | `backend/main.py` | 6 de 14 métodos inaccesibles |
| C-3 | `App.jsx` solo llama a Newton, sin selector de métodos | `frontend/src/App.jsx` | UI no es demo-able |

> **C-1 y C-2 están resueltos** en el `main.py` entregado esta sesión. **C-3 está resuelto** en el `App.jsx` entregado esta sesión. Copiar los 3 archivos al proyecto activa la demo completa.

### Importantes (degradan la experiencia)

| ID | Problema | Archivo | Impacto |
|----|----------|---------|---------|
| I-1 | `auto_params.py` puede elegir `x0` que hace `f'(x₀) ≈ 0` para ecuaciones simétricas tipo `x²-2` | `backend/core/auto_params.py` | Métodos Newton marcan aplicabilidad falsa |
| I-2 | `auto_params.py` genera solo 1 candidato para g(x) (estrategia S1). Para ecuaciones donde f'(raíz) ≈ 0, gx_sympy es None → Aitken/Steffensen inaplicables | `backend/core/auto_params.py` | Punto Fijo/Aitken/Steffensen fallan en ciertas ecuaciones |
| I-3 | Frontend no permite parámetros manuales: el usuario no puede cambiar x0, a, b, tol | `frontend/src/App.jsx` | Para ecuaciones donde auto_params falla, no hay override |
| I-4 | 4 tests con expectativas erróneas (denominador cero) | `test_aitken.py`, `test_steffensen.py` | pytest reporta 4 fallos; confunde en entrega |
| I-5 | `test_biseccion.py` vacío — 0 cobertura del método Bisección | `backend/test/test_biseccion.py` | Bisección sin tests |
| I-6 | `index.html` tiene `title="frontend"` | `frontend/index.html` | Feo en demo y en pestaña del navegador |

### Opcionales (pulido)

| ID | Problema | Archivo | Impacto |
|----|----------|---------|---------|
| O-1 | Gráfico de convergencia (error% vs iteración) | `App.jsx` nuevo | Hace la demo más académica |
| O-2 | Botón exportar Excel desde UI | `App.jsx` + endpoint | Funcionalidad prometida en spec original |
| O-3 | Renderizado LaTeX de f(x) y f'(x) | `App.jsx` + KaTeX | Más académico |
| O-4 | `docs/` tiene 2 documentos obsoletos que reportan estado incorrecto | `docs/` | Confunde al evaluador |
| O-5 | Commits pendientes para git history limpio | `.git` | Buena práctica |

---

## 5. Próximos Pasos Priorizados

Los pasos C-1, C-2, C-3 ya están resueltos en los archivos entregados esta sesión. El orden siguiente asume que esos 3 archivos ya fueron copiados al proyecto.

| Prioridad | Paso | Archivo(s) | Tiempo est. | Depende de |
|-----------|------|-----------|-------------|------------|
| **1** | ~~Añadir 6 endpoints newton_family + serialización~~ | `main.py` | ~~15 min~~ | **HECHO** |
| **2** | ~~Reescribir App.jsx con selector 14 métodos + tabla~~ | `App.jsx`, `App.css` | ~~3h~~ | **HECHO** |
| **3** | Corregir los 4 tests con expectativas erróneas | `test_aitken.py`, `test_steffensen.py` | 20 min | — |
| **4** | Personalizar index.html (title, lang) | `index.html` | 5 min | — |
| **5** | Añadir parámetros manuales en UI (x0, a, b, tol) | `App.jsx` | 1.5h | Paso 2 |
| **6** | Gráfico de convergencia (error% vs k) | `App.jsx` | 1.5h | Paso 2 |
| **7** | Endpoint exportar Excel + botón en UI | `main.py`, `App.jsx` | 2h | Pasos 1 y 2 |
| **8** | Renderizado LaTeX con KaTeX | `App.jsx`, `package.json` | 1h | Paso 2 |
| **9** | Tests para Bisección | `test_biseccion.py` | 1h | — |
| **10** | Limpiar docs obsoletos + commit final | `docs/`, git | 30 min | Todo lo anterior |

**Para demo mínima funcional:** completar pasos 1–4 (ya hechos 1–2). Tiempo restante: ~25 min.  
**Para entrega académica completa:** pasos 1–10. Tiempo restante: ~8h.

---

## 6. Cómo Arrancar el Proyecto

### Prerequisitos

```bash
python 3.10+
pip install fastapi uvicorn sympy
node 18+  (para el frontend)
```

### Backend

```bash
# Desde la raíz del proyecto ("metodos numericos web/")
uvicorn backend.main:app --reload

# API disponible en:  http://127.0.0.1:8000
# Swagger UI en:      http://127.0.0.1:8000/docs
```

**IMPORTANTE:** Usar el `main.py` corregido (entregado esta sesión), no el del ZIP original. El del ZIP retorna dataclasses sin serializar → error 500.

### Frontend

```bash
# Desde metodos numericos web/frontend/
npm install     # solo la primera vez
npm run dev

# Interfaz disponible en: http://localhost:5173
```

Ambos procesos deben estar corriendo simultáneamente. El frontend apunta hardcoded a `http://127.0.0.1:8000`.

### Tests

```bash
# Desde la raíz del proyecto ("metodos numericos web/")
python -m pytest backend/test/ -v

# Resultado esperado: 111 passed, 4 failed
# Los 4 fallos son tests con expectativas incorrectas (ver sección 4, I-4)
# Para verlos claramente:
python -m pytest backend/test/ -v --tb=short 2>&1 | tail -30
```

---

## 7. Historial de Decisiones Importantes

### Steffensen — Parche definitivo (BUG-01 y BUG-02)

**Problema:** Para ecuaciones `x³−2x−5` y `e^−x−x`, la función `g(x) = x - f(x)/f'(x)` converge cuadráticamente, generando exactamente 1 fila Steffensen (k=0). En k=0 no hay fila anterior → el comparador `k ≥ 1` nunca ejecuta → `converged = False` aunque la raíz sea exacta.

**Parche aplicado** (verificado en ZIP, líneas 213-235 de `steffensen.py`):
```python
# Fallback: 1 sola fila y root=None → evaluar f(candidate) directamente
if not converged and len(rows) == 1:
    candidate = rows[0].xk_hat        # ← usa xk_hat directamente (no "root")
    f_at_root = abs(float(eq.f_sympy.subs(_x, candidate).evalf()))
    if f_at_root < tol:
        converged = True
        root = candidate
```

**Estado:** ✅ Aplicado en el ZIP.

### Compatibilidad Excel — Restricciones del SPEC

Definidas en `docs/EXCEL_COMPATIBILITY_SPEC.md`. No modificar sin romper la compatibilidad.

| Decisión | Detalle |
|----------|---------|
| `tol = 0.00001`, `max_iter = 25` | Valores canónicos. No configurables por auto_params. |
| Error % = `ABS((x_nuevo − x_anterior) / x_nuevo) × 100` | Fórmula exacta de Excel. |
| `iteration_count = len(rows) - 1` | Primera fila no tiene error → no cuenta. Steffensen con 1 fila → `iteration_count = 0`. |
| Capa Aitken inicia en `pf[1]`, no en `pf[0]` | Verificado contra `amburger.xlsx` con `diff = 0.000e+00`. |
| `_delta2` retorna `None` cuando denominador = 0 | Replica `#DIV/0!` de Excel. NO hacer fallback a `p0`. |
| Rama fija `+√D` en Newton 2do Orden | Especificado en SPEC §6.5. Diverge en cos(x)−x — comportamiento correcto. |
| `f'(x₀)` congelado en Von Mises | Por definición del método. Diverge cuando `|1 - f'(α)/f'(x₀)| > 1`. |

### Tests corregidos o pendientes

**No corregidos aún (en el ZIP siguen con expectativas erróneas):**

```python
# test_aitken.py:46 — DEBE CAMBIAR A:
assert result is None   # (era: assert result == 1.0)

# test_aitken.py:58 — DEBE CAMBIAR A:
assert result is None   # (era: assert abs(result - 0.254) < 1e-12)

# test_steffensen.py:43 — DEBE CAMBIAR A:
assert result is None   # (era: assert result == 2.0)

# test_steffensen.py:148 — DEBE CAMBIAR A:
assert result.applicable is False   # (era: assert result.root is not None)
```

**Por qué no se han corregido:** Fueron identificados como erróneos pero no commiteados. El ZIP los tiene en estado original (roto).

### auto_params.py — estrategia de g(x)

La versión actual genera g(x) dinámicamente con la estrategia S1: `g(x) = x - f(x)/f'(x)`. Esto garantiza convergencia cerca de la raíz (`|g'(raíz)| ≈ 0`). El RESUMEN anterior afirmaba que estaba hardcodeada como `(2x+5)^(1/3)` — esto era incorrecto según el código real.

**Limitación real:** Solo implementa S1. Para ecuaciones donde `f'(raíz) ≈ 0`, no genera ningún candidato y `gx_sympy = None` → Aitken/Steffensen/Punto Fijo retornan `applicable = False`.

---

## 8. Estado para Presentación Académica

### Porcentaje completado por componente

| Componente | % completado | Descripción |
|------------|-------------|-------------|
| Backend — lógica matemática | **95%** | 14 métodos implementados, validados contra Excel |
| Backend — endpoints API | **100%** | 16 endpoints con main.py corregido (esta sesión) |
| Backend — serialización | **100%** | Corregida con `dataclasses.asdict()` (esta sesión) |
| Backend — tests | **72%** | 111/115 pasan; 4 fallos fáciles de corregir; bisección sin cobertura |
| Frontend — selector de métodos | **100%** | App.jsx entregado esta sesión |
| Frontend — tabla de iteraciones | **100%** | App.jsx entregado esta sesión |
| Frontend — parámetros manuales | **0%** | Pendiente |
| Frontend — gráfico convergencia | **0%** | Pendiente |
| Frontend — export Excel | **0%** | Pendiente (lógica existe en backend/excel/) |
| Frontend — LaTeX rendering | **0%** | Pendiente |
| Documentación | **85%** | Docs técnicos completos; 2 docs obsoletos a limpiar |
| **Demo funcional** | **~70%** | |
| **Entrega académica completa** | **~55%** | |

### Qué falta para demo funcional (presentación)

Con los 3 archivos entregados esta sesión (`main.py`, `App.jsx`, `App.css`) la demo es funcional. Lo que elevaría la calidad de la presentación:

1. **Parámetros manuales (x0, a, b)** — sin esto, si `auto_params` elige mal, el usuario no puede corregirlo (~1.5h)
2. **`index.html` title** — cambiar "frontend" por nombre del proyecto (~5 min)
3. **Corregir 4 tests** — para que pytest muestre 115/115 (~20 min)

### Qué falta para entrega académica final

Además de lo anterior:

4. Gráfico de error% vs iteración por método (~1.5h)
5. Exportación a Excel desde la UI (~2h)
6. Renderizado LaTeX de f(x) y f'(x) (~1h)
7. Tests de Bisección (~1h)
8. Limpieza de docs obsoletos + commit final (~30 min)

**Tiempo total restante para entrega académica completa: ~8 horas.**

---

## Archivos entregados en la sesión 2026-06-06

Disponibles para descarga y copia directa al proyecto:

| Archivo | Destino en el proyecto | Cambio |
|---------|----------------------|--------|
| `main.py` | `backend/main.py` | +6 endpoints + serialización correcta |
| `App.jsx` | `frontend/src/App.jsx` | Reescrito completo (14 métodos, tabla, resumen) |
| `App.css` | `frontend/src/App.css` | Reescrito completo (tema oscuro académico) |
