# PROJECT_STATE_MASTER.md

**Proyecto:** Métodos Numéricos Web  
**Fecha de verificación:** 2026-06-06  
**Fuente única:** Contenido real del ZIP `metodos_numericos_web.zip`  
**Principio:** Cada afirmación en este documento fue verificada directamente en archivos del ZIP.  
Cuando un documento interno del proyecto contradice el código, prevalece el código.

---

## ESTADO REAL VERIFICADO

### Qué EXISTE en el ZIP (verificado archivo por archivo)

**Backend — archivos presentes y funcionales:**

| Archivo | Existe | Funcional | Notas |
|---------|--------|-----------|-------|
| `backend/main.py` | ✅ | ⚠️ parcial | 10 endpoints; sin serialización; falta newton_family |
| `backend/core/auto_params.py` | ✅ | ✅ | Genera parámetros dinámicamente |
| `backend/core/equation_parser.py` | ✅ | ✅ | Parsea a sympy, LaTeX, Excel |
| `backend/core/sympy_to_excel.py` | ✅ | ✅ | Conversión de expresiones |
| `backend/methods/biseccion.py` | ✅ | ✅ | |
| `backend/methods/regula_falsi.py` | ✅ | ✅ | |
| `backend/methods/punto_fijo.py` | ✅ | ✅ | |
| `backend/methods/aitken.py` | ✅ | ✅ | |
| `backend/methods/steffensen.py` | ✅ | ✅ | Parche definitivo aplicado |
| `backend/methods/newton_raphson.py` | ✅ | ✅ | |
| `backend/methods/von_mises.py` | ✅ | ✅ | |
| `backend/methods/secante.py` | ✅ | ✅ | |
| `backend/methods/newton_family.py` | ✅ | ✅ | 6 funciones implementadas; sin endpoints |
| `backend/schemas/models.py` | ✅ | ✅ | Dataclasses para resultados |
| `backend/excel/excel_generator.py` | ✅ | ✅ | Sin endpoint HTTP expuesto |
| `backend/excel/excel_styles.py` | ✅ | ✅ | |
| `backend/excel/excel_templates.py` | ✅ | ✅ | |
| `backend/test/conftest.py` | ✅ | ✅ | Fixtures para `x^3-4x+1` |
| `backend/test/test_newton_family.py` | ✅ | ✅ | 40 tests, 0 fallos |
| `backend/test/test_regula_falsi.py` | ✅ | ✅ | 20 tests, 0 fallos |
| `backend/test/test_newton_raphson.py` | ✅ | ✅ | 18 tests, 0 fallos |
| `backend/test/test_aitken.py` | ✅ | ⚠️ | 19 tests, **2 fallos** (expectativas erróneas) |
| `backend/test/test_steffensen.py` | ✅ | ⚠️ | 18 tests, **2 fallos** (expectativas erróneas) |
| `backend/test/test_biseccion.py` | ✅ | ❌ | **Archivo vacío — 0 tests** |

**Frontend — archivos presentes:**

| Archivo | Existe | Estado |
|---------|--------|--------|
| `frontend/src/App.jsx` | ✅ | ⚠️ **Prototipo de 69 líneas — solo llama a Newton** |
| `frontend/src/App.css` | ✅ | ⚠️ **CSS default de Vite — no es diseño del proyecto** |
| `frontend/src/main.jsx` | ✅ | ✅ Correcto, no modificar |
| `frontend/src/index.css` | ✅ | ✅ OK |
| `frontend/index.html` | ✅ | ⚠️ `<title>frontend</title>` — sin personalizar |
| `frontend/package.json` | ✅ | ✅ React 19 + Vite 8 |
| `frontend/vite.config.js` | ✅ | ✅ Configuración mínima correcta |
| `frontend/src/components/` | ✅ | ❌ **Directorio vacío** |
| `frontend/src/pages/` | ✅ | ❌ **Directorio vacío** |
| `frontend/src/services/` | ✅ | ❌ **Directorio vacío** |

**Documentación:**

| Archivo | Estado | Confiabilidad |
|---------|--------|---------------|
| `docs/EXCEL_COMPATIBILITY_SPEC.md` | ✅ Normativo | Alta — fuente de verdad para fórmulas |
| `docs/FINAL_DELIVERY_AUDIT.md` | ✅ Válido | Alta — describe estado real |
| `docs/REGRESSION_TESTS.md` | ✅ Válido | Alta |
| `docs/RESIDUAL_METHODS_AUDIT.md` | ✅ Válido | Alta |
| `docs/TEST_CLEANUP_REPORT.md` | ✅ Válido | Alta |
| `docs/AUTO_PARAMS_CURRENT_STATE.md` | ⚠️ Parcial | Media — describe versión anterior de auto_params |
| `docs/MULTI_EQUATION_CURRENT_AUDIT.md` | ✅ Válido | Alta |
| `docs/DELIVERY_CHECKLIST.md` | ❌ Incorrecto | Baja — afirma 115/115 PASS; son 111/115 |
| `docs/AUDITORIA_FINAL_2026-06-06.md` | ⚠️ Obsoleto | Media — estado intermedio |
| `docs/INFORME_AUDITORIA_FINAL.md` | ⚠️ Obsoleto | Media — redundante |
| `PROJECT_STATUS_2026-06-06.md` | ⚠️ Desactualizado | Baja — describe auto_params antes de la versión actual |

### Qué NO EXISTE en el ZIP

| Ítem | Documentado como existente en | Realidad |
|------|-------------------------------|----------|
| 6 endpoints de newton_family en `main.py` | `RESUMEN_PROYECTO.md` | **No están registrados** |
| Serialización con `dataclasses.asdict()` en `main.py` | implícito | **No existe — error 500 en producción** |
| UI completa con selector de 14 métodos | `RESUMEN_PROYECTO.md` | **Solo Newton-Raphson en App.jsx** |
| `components/`, `pages/`, `services/` con contenido | `RESUMEN_PROYECTO.md` | **Vacíos** |
| Tabla de iteraciones en frontend | `RESUMEN_PROYECTO.md` | **No existe** |
| Tema oscuro en App.css | `RESUMEN_PROYECTO.md` | **CSS default de Vite** |
| `requirements.txt` | — | **No existe** |
| Endpoint `/method/export_excel` | `Archivo 00_PROYECTO_GENERAL.md` | **No existe** |

### Qué está documentado pero falta implementar

1. Exportación a Excel desde la UI (la lógica existe en `backend/excel/` pero sin endpoint ni botón)
2. Parámetros manuales en el frontend (x0, a, b, tol)
3. Gráfico de convergencia (error % vs iteración)
4. Renderizado LaTeX de f(x) y f'(x) en la UI
5. Tests de Bisección (archivo vacío)
6. Corrección de los 4 tests con expectativas erróneas

---

## LISTA DE ARCHIVOS CRÍTICOS

Archivos que no deben modificarse sin entender sus contratos:

| Archivo | Por qué es crítico |
|---------|-------------------|
| `docs/EXCEL_COMPATIBILITY_SPEC.md` | Define tol, max_iter, fórmula de error, `iteration_count`. Toda decisión matemática se justifica aquí. |
| `backend/schemas/models.py` | Contrato de datos entre métodos y API. Cambiar campos rompe tests y serialización. |
| `excel_templates/amburger.xlsx` | Fuente de verdad Excel. Valor de referencia: diff = 0.000e+00 para los 14 métodos. |
| `backend/core/equation_parser.py` | Parser de ecuaciones. No modificar — todos los métodos dependen de `ParsedEquation`. |
| `backend/test/conftest.py` | Fixtures de tests. Ecuación de referencia: `x^3 - 4*x + 1`. No cambiar fixtures existentes. |
| `backend/methods/steffensen.py` | Contiene parche definitivo para BUG-01 y BUG-02. Ver sección de decisiones. |
| `backend/methods/newton_family.py` | 6 métodos de alta orden. Congelado — validado contra Excel. |

---

## LISTA DE ENDPOINTS REALES

### En el ZIP (main.py actual)

```
GET  /                          → {"mensaje": "...", "endpoints": 8}
POST /analyze                   → {f_latex, fp_latex, f_excel, fp_excel}
POST /method/newton             → MethodResult (Newton-Raphson)
POST /method/biseccion          → MethodResult
POST /method/regula_falsi       → MethodResult
POST /method/secante            → MethodResult
POST /method/punto_fijo         → MethodResult
POST /method/steffensen         → MethodResult
POST /method/aitken             → MethodResult
POST /method/von_mises          → MethodResult
```

**Total: 10 endpoints. Problema: retornan dataclass directamente → TypeError en producción.**

### Con el main.py corregido (entregado 2026-06-06)

Los 10 anteriores más:

```
POST /method/newton_modificado    → MethodResult
POST /method/newton_segundo_orden → MethodResult
POST /method/chebyshev            → MethodResult
POST /method/halley               → MethodResult
POST /method/super_halley         → MethodResult
POST /method/ostrowsky            → MethodResult
```

**Total: 16 endpoints. Todos con `dataclasses.asdict()` para serialización correcta.**

### Formato de request (todos los endpoints de método)

```json
POST /method/{nombre}
Content-Type: application/json

{ "equation": "x^3 - 2*x - 5" }
```

### Formato de response (MethodResult serializado)

```json
{
  "method_name": "Newton-Raphson",
  "applicable": true,
  "reason": "f'(x₀) ≠ 0",
  "equation_str": "x^3 - 2*x - 5",
  "f_latex": "x^{3} - 2 x - 5",
  "fp_latex": "3 x^{2} - 2",
  "fpp_latex": "6 x",
  "params_used": {"x0": 2.0, "tol": 0.00001, "equation": "x^3 - 2*x - 5"},
  "iterations": [
    {"k": 0, "xk": 2.0, "fxk": -1.0, "fpxk": 10.0, "x_new": 2.1, "error_pct": null, "converged": null},
    ...
  ],
  "root": 2.0945514815...,
  "final_error_pct": 3.2e-7,
  "converged": true,
  "iteration_count": 4,
  "excel_sheet_name": "Newton-Raphson",
  "formula_description": "xₙ₊₁ = xₙ − f(xₙ)/f'(xₙ)"
}
```

---

## LISTA DE MÉTODOS REALES

### 14 métodos implementados y validados contra amburger.xlsx

| # | Método | Archivo | Grupo | Endpoint disponible |
|---|--------|---------|-------|---------------------|
| 1 | Bisección | `biseccion.py` | Intervalo | ✅ en ZIP |
| 2 | Regula Falsi | `regula_falsi.py` | Intervalo | ✅ en ZIP |
| 3 | Punto Fijo | `punto_fijo.py` | Punto Fijo | ✅ en ZIP |
| 4 | Aitken (Δ²) | `aitken.py` | Punto Fijo | ✅ en ZIP |
| 5 | Steffensen | `steffensen.py` | Punto Fijo | ✅ en ZIP |
| 6 | Newton-Raphson | `newton_raphson.py` | Derivada | ✅ en ZIP |
| 7 | Von Mises | `von_mises.py` | Derivada | ✅ en ZIP |
| 8 | Secante | `secante.py` | Derivada | ✅ en ZIP |
| 9 | Newton Modificado | `newton_family.py` | Familia Newton | ❌ falta en ZIP main.py |
| 10 | Newton 2do Orden | `newton_family.py` | Familia Newton | ❌ falta en ZIP main.py |
| 11 | Chebyshev | `newton_family.py` | Familia Newton | ❌ falta en ZIP main.py |
| 12 | Halley | `newton_family.py` | Familia Newton | ❌ falta en ZIP main.py |
| 13 | Super Halley | `newton_family.py` | Familia Newton | ❌ falta en ZIP main.py |
| 14 | Ostrowsky | `newton_family.py` | Familia Newton | ❌ falta en ZIP main.py |

### Columnas de iteraciones por tipo de método

| Tipo | Columnas en `iterations[]` |
|------|---------------------------|
| Bisección / Regula Falsi | `k, a, c, b, fa, fc, fb, fa_fc, error_pct, converged` |
| Punto Fijo | `k, xk, gxk, x_new, error_pct, converged` |
| Aitken / Steffensen | `k, p0, p1, p2, xk_hat, x_new, error_pct, converged` |
| Newton-Raphson | `k, xk, fxk, fpxk, x_next, error_pct, converged` |
| Familia Newton | `k, xk, fxk, fpxk, fppxk, x_next, error_pct, converged` |
| Secante | `k, xk_prev, xk, fxk, x_new, error_pct, converged` |
| Von Mises | `k, xk, fxk, fp_x0, x_new, error_pct, converged` |

---

## ESTADO DE TESTS

### Resumen

```
pytest backend/test/
→ 115 collected
→ 111 passed
→  4 failed
→  0 errors
```

### Detalle por archivo

| Archivo | Collected | Pass | Fail | Notas |
|---------|-----------|------|------|-------|
| `test_newton_family.py` | 40 | 40 | 0 | ✅ completo |
| `test_regula_falsi.py` | 20 | 20 | 0 | ✅ completo |
| `test_newton_raphson.py` | 18 | 18 | 0 | ✅ completo |
| `test_aitken.py` | 19 | 17 | **2** | expectativas erróneas |
| `test_steffensen.py` | 18 | 16 | **2** | expectativas erróneas |
| `test_biseccion.py` | **0** | — | — | **archivo vacío** |

### Los 4 tests que fallan — corrección exacta

```python
# test_aitken.py:46
# ACTUAL:   assert result == 1.0
# CORRECTO: assert result is None
# MOTIVO: _aitken_delta2(1.0, 1.0, 1.0) → denom=0 → None (replica #DIV/0! Excel)

# test_aitken.py:58
# ACTUAL:   assert abs(result - 0.254) < 1e-12
# CORRECTO: assert result is None
# MOTIVO: misma razón — secuencia constante → denom=0

# test_steffensen.py:43
# ACTUAL:   assert result == 2.0
# CORRECTO: assert result is None
# MOTIVO: _delta2(2.0, 2.0, 2.0) → denom=0 → None (mismo patrón)

# test_steffensen.py:148
# ACTUAL:   assert result.root is not None
# CORRECTO: assert result.applicable is False
# MOTIVO: cuando applicable=False, root=None por diseño de MethodResult
```

### Ecuación de referencia usada en conftest.py

```python
f(x) = x^3 - 4*x + 1
# Raíces: -2.114908, 0.254102, 1.860806
# Cambio de signo en: [0,1], [1,2], [-3,-2]
# x0 estándar en tests: 1.0
# tol estándar en tests: 0.00001
# max_iter estándar: 25
```

---

## ESTADO FRONTEND

### Situación actual (ZIP real)

`frontend/src/App.jsx` contiene 69 líneas con un prototipo mínimo que:
- Tiene un input de texto para la ecuación
- Tiene un botón "Analizar" que siempre llama a `/method/newton`
- Muestra 4 campos del resultado: raíz, iteraciones, convergió, error
- No tiene selector de método
- No tiene tabla de iteraciones
- No tiene manejo de errores
- No tiene ejemplos de ecuaciones

`frontend/src/App.css` es el CSS default generado por Vite (`create-react-app`-style). No es diseño del proyecto.

### Dependencias instaladas (package.json)

```json
"dependencies": {
  "react": "^19.2.6",
  "react-dom": "^19.2.6"
}
```

No hay: KaTeX, Chart.js, Recharts, ni ninguna librería de UI.

### Frontend corregido (generado 2026-06-06, no en ZIP)

Los archivos `App.jsx` (385 líneas) y `App.css` (467 líneas) fueron generados en esta sesión e incluyen:
- Selector de 14 métodos agrupados por familia con colores
- 6 ecuaciones de ejemplo clickeables
- Tarjeta de resumen (raíz, convergió, iteraciones, error)
- Tabla de iteraciones con columnas específicas por método
- Manejo de errores de red con instrucción de arranque
- Tema oscuro académico con fuentes JetBrains Mono + Libre Baskerville

---

## ESTADO BACKEND

### Problema crítico #1 — Serialización

El `main.py` del ZIP retorna objetos `MethodResult` (dataclass) directamente desde los handlers de FastAPI:

```python
# ZIP actual — ROTO:
result = run_newton(eq, params)
return result   # TypeError: Object of type MethodResult is not JSON serializable
```

Corrección necesaria en cada handler:
```python
import dataclasses
return dataclasses.asdict(result)
```

### Problema crítico #2 — Endpoints faltantes

Las 6 funciones de `newton_family.py` existen y están implementadas, pero no hay ningún `@app.post` en `main.py` que las exponga. Ver sección de endpoints.

### auto_params.py — comportamiento real (verificado en código)

La versión actual (timestamp `15:10`, más reciente que `PROJECT_STATUS` de `14:56`) usa generación dinámica:

**g(x):** Estrategia S1 únicamente → `g(x) = x - f(x)/f'(x)`. Solo 1 candidato. Si `f'(raíz) ≈ 0`, no genera g(x) y `gx_sympy = None` → Aitken/Steffensen/Punto Fijo retornan `applicable = False`.

**x0:** `_best_integer_near(raíz)` con penalización para puntos donde `|f'(x₀)| < 1e-10`. Prefiere enteros positivos → cero → negativos.

**numpy:** Importado pero no usado. `import numpy as np` está presente sin ninguna llamada a `np.*`. Es deuda técnica menor.

### Constantes globales (congeladas por EXCEL_COMPATIBILITY_SPEC)

```python
_TOLERANCE = 0.00001   # en todos los métodos
_MAX_ITER = 25         # en todos los métodos
# Error %: ABS((x_nuevo - x_anterior) / x_nuevo) * 100
# iteration_count = len(rows) - 1
```

---

## PRÓXIMO PASO RECOMENDADO

**Paso inmediato para tener demo funcional:**

Copiar los 3 archivos generados el 2026-06-06 al proyecto:

```
backend/main.py          ← +6 endpoints + dataclasses.asdict()
frontend/src/App.jsx     ← UI completa 14 métodos
frontend/src/App.css     ← tema oscuro académico
```

Luego arrancar (ver sección "Cómo arrancar").

**Siguiente paso de desarrollo (después de la demo):**

Agregar parámetros manuales en el frontend. El mayor problema de usabilidad actual es que el usuario no puede corregir el `x0`, `a` o `b` cuando `auto_params` elige mal. Solución: añadir campos opcionales en la UI que sobrescriban los parámetros automáticos en el request body.

---

## RIESGOS CONOCIDOS

| ID | Riesgo | Severidad | Mitigación |
|----|--------|-----------|------------|
| R-1 | `main.py` sin serialización → error 500 en todos los endpoints | **Crítica** | Usar main.py corregido de esta sesión |
| R-2 | `auto_params` elige `x0` cerca de raíz con `f'(x₀) ≈ 0` | Alta | Parámetros manuales en UI (pendiente) |
| R-3 | `auto_params` genera solo S1 para g(x); ecuaciones con `f'(raíz) ≈ 0` dejan Aitken/Steffensen inaplicables | Alta | Implementar estrategias S2–S4 (pendiente) |
| R-4 | 4 tests fallan → pytest no da 115/115 limpio en entrega | Media | Corregir 4 aserciones (~20 min) |
| R-5 | `numpy` importado sin uso en auto_params → advertencia y dependencia innecesaria | Baja | Eliminar el import |
| R-6 | `PROJECT_STATUS_2026-06-06.md` describe auto_params desactualizado y puede confundir | Baja | No leer ese archivo; leer código directamente |
| R-7 | Von Mises diverge en `x³-x-1`; Newton 2do Orden diverge en `cos(x)-x` y `e^-x-x` | Baja | Documentado en RESIDUAL_METHODS_AUDIT.md — son limitaciones matemáticas, no bugs |
| R-8 | Bisección sin tests | Baja | Escribir test_biseccion.py |
| R-9 | `index.html` con title="frontend" | Muy baja | Cambiar en 1 línea |

---

## CHECKLIST PARA DEMO

Pasos mínimos para una demo funcional en navegador:

- [ ] **Reemplazar `backend/main.py`** con versión corregida (+6 endpoints + serialización)
- [ ] **Reemplazar `frontend/src/App.jsx`** con versión completa (14 métodos, tabla)
- [ ] **Reemplazar `frontend/src/App.css`** con tema oscuro
- [ ] Instalar dependencias Python: `pip install fastapi uvicorn sympy`
- [ ] Arrancar backend: `uvicorn backend.main:app --reload`
- [ ] Instalar dependencias Node: `cd frontend && npm install`
- [ ] Arrancar frontend: `npm run dev`
- [ ] Verificar en `http://localhost:5173` que el selector muestra 14 métodos
- [ ] Probar con ecuación `x^3 - 2*x - 5` → Newton-Raphson → debe mostrar raíz ≈ 2.0946
- [ ] Probar con método Halley → debe converger en ≤ 3 iteraciones
- [ ] Verificar que la tabla de iteraciones se renderiza con columnas correctas

**Tiempo estimado para completar checklist: 30 minutos** (suponiendo que los 3 archivos corregidos ya están disponibles).

---

## CHECKLIST PARA ENTREGA FINAL

Todo lo del checklist de demo, más:

- [ ] Corregir los 4 tests con expectativas erróneas (ver sección Tests)
- [ ] Ejecutar `pytest backend/test/` → verificar 115/115 PASS
- [ ] Cambiar `<title>frontend</title>` en `index.html`
- [ ] Añadir parámetros manuales en UI (x0, a, b, tol)
- [ ] Añadir gráfico de convergencia (error% vs iteración)
- [ ] Añadir endpoint `POST /method/export_excel` en main.py
- [ ] Añadir botón "Exportar Excel" en App.jsx
- [ ] Instalar y configurar KaTeX para renderizar f_latex / fp_latex
- [ ] Escribir tests para Bisección en test_biseccion.py
- [ ] Eliminar `import numpy as np` sin uso de auto_params.py
- [ ] Mover `docs/AUDITORIA_FINAL_2026-06-06.md` y `docs/INFORME_AUDITORIA_FINAL.md` a `docs/archive/`
- [ ] Hacer commit con mensaje descriptivo del estado final
- [ ] Verificar que `git status` queda limpio

**Tiempo estimado: 8 horas adicionales después de la demo.**

---

## CÓMO ARRANCAR EL PROYECTO

### Backend

```bash
# Desde el directorio raíz del proyecto ("metodos numericos web/")
pip install fastapi uvicorn sympy

# IMPORTANTE: usar el main.py corregido, no el del ZIP original
uvicorn backend.main:app --reload

# Verificación rápida:
curl -s http://127.0.0.1:8000/ | python3 -m json.tool
# → debe mostrar {"mensaje": "...", "endpoints": 14}

# Swagger UI interactivo:
# http://127.0.0.1:8000/docs

# Prueba de un método:
curl -s -X POST http://127.0.0.1:8000/method/newton \
  -H "Content-Type: application/json" \
  -d '{"equation": "x^3 - 2*x - 5"}' | python3 -m json.tool | grep root
```

### Frontend

```bash
# Desde "metodos numericos web/frontend/"
npm install    # solo primera vez
npm run dev

# Disponible en: http://localhost:5173
# IMPORTANTE: el backend debe estar corriendo simultáneamente
```

### Tests

```bash
# Desde "metodos numericos web/" (raíz del proyecto)
python -m pytest backend/test/ -v

# Resultado esperado CON el ZIP sin modificar:
# 111 passed, 4 failed

# Resultado esperado DESPUÉS de corregir los 4 tests:
# 115 passed, 0 failed

# Ver solo los fallos:
python -m pytest backend/test/ -v --tb=short 2>&1 | grep -E "FAILED|PASSED|ERROR" | tail -20
```

---

## DECISIONES TÉCNICAS REGISTRADAS

### 1. Steffensen — Parche fallback (BUG-01, BUG-02)

**Contexto:** Para ecuaciones donde `g(x) = x - f(x)/f'(x)` (Newton-like), la secuencia de Punto Fijo converge cuadráticamente. Esto produce exactamente 1 fila Steffensen (k=0). En k=0 no hay fila anterior, por lo que el comparador `k ≥ 1` nunca ejecuta → `converged = False` aunque la raíz sea exacta.

**Decisión:** Cuando `len(rows) == 1` y `converged == False`, evaluar `|f(rows[0].xk_hat)|` directamente. Si es menor que `tol`, marcar como convergido.

**Código clave** (`steffensen.py`, líneas ~213-235):
```python
if not converged and len(rows) == 1:
    candidate = rows[0].xk_hat        # clave: usar xk_hat, no root
    f_at_root = abs(float(eq.f_sympy.subs(_x, candidate).evalf()))
    if f_at_root < tol:
        converged = True
        root = candidate
```

**Estado:** ✅ Aplicado en el ZIP.

### 2. Compatibilidad Excel — Reglas congeladas

Definidas en `EXCEL_COMPATIBILITY_SPEC.md`. **No modificar** sin romper la compatibilidad verificada (diff = 0.000e+00 contra amburger.xlsx):

| Regla | Valor | Consecuencia si se cambia |
|-------|-------|--------------------------|
| Tolerancia | `0.00001` | Número de iteraciones cambia |
| Máx iteraciones | `25` | Tablas de diferente longitud que Excel |
| Fórmula error | `ABS((nuevo - anterior) / nuevo) * 100` | Valores de error distintos |
| `iteration_count` | `len(rows) - 1` | Conteo off-by-one vs Excel |
| Capa Aitken | inicia en `pf[1]`, no `pf[0]` | Error ≈ 2.4e-3 vs amburger.xlsx |
| `_delta2` → denom=0 | retorna `None` | Rompe tests; cambia comportamiento vs Excel |
| Newton 2do Orden rama | `+√D` fija | Diverge en cos(x)-x — es correcto según SPEC |

### 3. Limitaciones matemáticas inherentes (no son bugs)

Estos métodos no convergen en ciertos casos por razones matemáticas, no por errores de implementación:

| Método | Ecuación | Causa |
|--------|----------|-------|
| Von Mises | `x³-x-1` | `f'(x₀)` congelado; `|1 - f'(α)/f'(x₀)| = 1.13 > 1` |
| Newton 2do Orden | `cos(x)-x` | Rama `+√D` apunta a raíz alejada desde x₀=1 |
| Newton 2do Orden | `e^-x-x` | Primer paso salta a x≈8.87; f''≈0 → paso ≈14285 |
| Ostrowsky | `cos(x)-x`, `e^-x-x`, `x⁴-10` | Escapa cuenca de convergencia |

### 4. auto_params.py — Estado actual del código

La versión en el ZIP (timestamp `15:10`) implementa:
- **g(x):** Solo estrategia S1: `g(x) = x - f(x)/f'(x)`
- **x0:** Entero más cercano a la raíz, evitando `f'(x₀) ≈ 0`
- **[a, b]:** Par de cambio de signo con enteros más pequeños
- **numpy:** Importado pero no usado (deuda técnica)

El archivo `PROJECT_STATUS_2026-06-06.md` dice que g(x) está hardcodeada como `(2x+5)^(1/3)` — esto es incorrecto. Ese documento describe una versión anterior. El código actual usa S1 dinámico.

---

## PROMPT PARA CONTINUAR EN UN CHAT NUEVO

Copiar y pegar exactamente el siguiente texto al iniciar una nueva conversación:

---

```
Estoy trabajando en un proyecto llamado "Métodos Numéricos Web". 
Necesito que leas el archivo PROJECT_STATE_MASTER.md que te adjunto como contexto maestro antes de hacer cualquier cosa.

CONTEXTO DEL PROYECTO (del PROJECT_STATE_MASTER.md):

**Stack:** Python 3.10+ / FastAPI / uvicorn / sympy (backend) + React 19 / Vite 8 (frontend)
**Ubicación:** directorio raíz = "metodos numericos web/"

**Estado actual verificado:**
- Backend: 14 métodos numéricos implementados y validados contra amburger.xlsx
- main.py en ZIP: 10 endpoints, sin serialización (necesita corrección)
- main.py corregido: 16 endpoints con dataclasses.asdict() — generado el 2026-06-06
- App.jsx en ZIP: 69 líneas, solo llama a Newton — prototipo mínimo
- App.jsx corregido: 385 líneas, selector 14 métodos, tabla de iteraciones — generado el 2026-06-06
- Tests: 111/115 pasan; 4 fallan por expectativas erróneas (ver detalle en PROJECT_STATE_MASTER.md)
- Frontend components/, pages/, services/ están vacíos

**Archivos críticos que NO debo modificar sin entender sus contratos:**
- docs/EXCEL_COMPATIBILITY_SPEC.md (fuente de verdad matemática)
- backend/schemas/models.py (contrato de datos)
- excel_templates/amburger.xlsx (referencia Excel)
- backend/test/conftest.py (fixtures de tests)

**Reglas del proyecto:**
- tol = 0.00001, max_iter = 25 (congelados por EXCEL_COMPATIBILITY_SPEC)
- Error % = ABS((nuevo - anterior) / nuevo) * 100
- iteration_count = len(rows) - 1
- _delta2 con denom=0 retorna None (NO hacer fallback a p0)
- Rama +√D fija en Newton 2do Orden (según SPEC §6.5)

**Para arrancar:**
- Backend: uvicorn backend.main:app --reload (desde "metodos numericos web/")
- Frontend: cd frontend && npm install && npm run dev
- Tests: python -m pytest backend/test/ -v

**Lo que necesito hacer ahora:** [DESCRIBE AQUÍ TU PRÓXIMA TAREA]

Por favor, antes de hacer cualquier cambio, confirma que entendiste el estado del proyecto leyendo este contexto. No asumas nada que no esté verificado aquí.
```

---

*Este documento fue generado el 2026-06-06 verificando el contenido real del ZIP `metodos_numericos_web.zip`. Sustituye a cualquier RESUMEN_PROYECTO anterior.*
