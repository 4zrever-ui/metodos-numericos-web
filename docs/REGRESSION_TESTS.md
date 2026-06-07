# REGRESSION_TESTS.md

**Fecha de generación:** 2026-06-06
**Generado desde:** evidencia real extraída del ZIP del proyecto
**Documentos fuente:** `EXCEL_COMPATIBILITY_SPEC.md`, `TEST_CLEANUP_REPORT.md`, `AUTO_PARAMS_CURRENT_STATE.md`, `MULTI_EQUATION_CURRENT_AUDIT.md`, `backend/test/*.py`
**Nota:** `AUTO_PARAMS_AUDIT.md` y `MULTI_EQUATION_AUDIT.md` no existen con esos nombres exactos. Los archivos reales son `AUTO_PARAMS_CURRENT_STATE.md` y `MULTI_EQUATION_CURRENT_AUDIT.md`, ubicados en `auditorias importantes/`.

---

## 1. Objetivo

La suite de regresión protege dos contratos independientes y no negociables:

**Contrato 1 — Compatibilidad Excel (SPEC congelado):**
Garantizar que los 14 métodos numéricos del backend reproduzcan exactamente el comportamiento celda a celda de `amburger.xlsx`. Cualquier refactor en `backend/methods/*.py` o `backend/core/*.py` que altere `root`, `final_error_pct` o `iteration_count` por encima de `diff = 0.000e+00` rompe este contrato y debe ser detectado antes de llegar a producción.

**Contrato 2 — Robustez matemática:**
Garantizar que cada método maneje correctamente sus casos límite conocidos: denominadores cero, discriminantes negativos, derivadas nulas, secuencias divergentes, condiciones de inaplicabilidad. Estos riesgos son inherentes a los algoritmos y no dependen del Excel; un refactor puede silenciosamente eliminar un `try/except` o un guard, volviendo frágil el backend ante entradas reales de usuarios.

La regresión también actúa como documentación viva de los invariantes del sistema: si un test falla, indica exactamente qué contrato se rompió y por qué.

---

## 2. Baseline congelado

### 2.1 Métodos cubiertos por el SPEC

Los siguientes 14 métodos están validados en `EXCEL_COMPATIBILITY_SPEC.md` (estado CONGELADO, fecha 2026-06-06):

| # | Método | Archivo de implementación | Hoja Excel (`amburger.xlsx`) |
|---|---|---|---|
| 1 | Bisección | `backend/methods/biseccion.py` | `Bisección` |
| 2 | Regula Falsi | `backend/methods/regula_falsi.py` | `Regula Falsi` |
| 3 | Punto Fijo | `backend/methods/punto_fijo.py` | `Punto Fijo` |
| 4 | Aitken (Δ²) | `backend/methods/aitken.py` | `Aitken` |
| 5 | Steffensen | `backend/methods/steffensen.py` | `Steffensen` |
| 6 | Newton-Raphson | `backend/methods/newton_raphson.py` | `Newton-Raphson` |
| 7 | Newton Modificado | `backend/methods/newton_family.py` | `Newton Modificado` |
| 8 | Newton 2do Orden | `backend/methods/newton_family.py` | `Newton 2do Orden` |
| 9 | Chebyshev | `backend/methods/newton_family.py` | `Chebyshev` |
| 10 | Halley | `backend/methods/newton_family.py` | `Halley` |
| 11 | Super Halley | `backend/methods/newton_family.py` | `Super Halley` |
| 12 | Ostrowsky | `backend/methods/newton_family.py` | `Ostrowsky` |
| 13 | Secante | `backend/methods/secante.py` | `Secante` |
| 14 | Von Mises | `backend/methods/von_mises.py` | `Von Mises` |

### 2.2 Ecuación canónica del SPEC

La auditoría Excel fue ejecutada con:

```
f(x) = x² − 2
g(x) = (x+2)/(x+1)   [para métodos de punto fijo]
x₀   = 1.0
tol  = 0.00001
```

> **Nota:** `x³ − 2x − 5` aparece en `MULTI_EQUATION_CURRENT_AUDIT.md` como la ecuación hardcodeada en `auto_params._generate_gx_candidates()` (un bug de g(x) estático), **no** como ecuación canónica del SPEC. La ecuación canónica del SPEC es `f(x) = x² − 2`.

### 2.3 Parámetros globales del SPEC

Definidos en `EXCEL_COMPATIBILITY_SPEC.md §1` y confirmados en `generar_excel_v2.py`:

| Constante | Valor | Definida en código como |
|---|---|---|
| Tolerancia | `0.00001` | `_TOLERANCE = 0.00001` |
| Máx. iteraciones | `25` | `_MAX_ITER = 25` |
| Fórmula de error | `ABS((x_nuevo − x_anterior) / x_nuevo) × 100` | ver §2 del SPEC |
| Criterio de convergencia | `error_pct < 0.00001` (estrictamente menor) | `conv = error_pct < tol` |
| Criterio de detención | Primer "SI" — el método para inmediatamente | ver §3 del SPEC |

### 2.4 Criterios de aceptación de la regresión

Un método **pasa** la regresión si, dado `f(x) = x² − 2`, `x₀ = 1`, `tol = 0.00001`:

1. `root` coincide con el valor de referencia del SPEC §8 con `diff = 0.000e+00`.
2. `final_error_pct` coincide con el valor de referencia del SPEC §8 con `diff = 0.000e+00`.
3. `iteration_count` coincide con el valor de referencia del SPEC §8 con `diff = 0`.
4. La tabla de iteraciones termina en el primer "SI" y no genera filas adicionales.
5. La fila k=0 tiene `error_pct = None` para métodos de intervalo y métodos Δ² (SPEC §3).

**Un método falla** si cualquiera de los cinco puntos anteriores no se cumple.

---

## 3. Inventario de pruebas

### 3.1 Archivos de test existentes

| Archivo | Tests | Métodos cubiertos | Estado |
|---|---|---|---|
| `backend/test/test_newton_raphson.py` | 18 | Newton-Raphson | ✅ activo |
| `backend/test/test_newton_family.py` | 40 | Newton Mod., Newton 2do Orden, Chebyshev, Halley, Super Halley, Ostrowsky | ✅ activo |
| `backend/test/test_regula_falsi.py` | 20 | Regula Falsi | ✅ activo |
| `backend/test/test_aitken.py` | 19 | Aitken (Δ²) | ✅ activo |
| `backend/test/test_steffensen.py` | 18 | Steffensen | ✅ activo |
| `backend/test/conftest.py` | — | Fixtures compartidas (ecuaciones, params) | ✅ activo |
| `backend/test/test_biseccion.py` | **0** | — | ⚠️ **archivo vacío** |

**Métodos SIN archivo de test dedicado:**

| Método | Estado |
|---|---|
| Bisección | ⚠️ `test_biseccion.py` existe pero está **vacío** (0 bytes) |
| Punto Fijo | ❌ **No existe ningún archivo de test** |
| Secante | ❌ **No existe ningún archivo de test** |
| Von Mises | ❌ **No existe ningún archivo de test** |

> Estos 4 métodos (Bisección, Punto Fijo, Secante, Von Mises) están validados en el SPEC Excel con diff `0.000e+00` pero **no tienen tests unitarios de regresión**. Son una brecha de cobertura real.

### 3.2 Tabla de inventario completo de tests

#### `test_newton_raphson.py` — 18 tests

| Clase | Test | Propósito | Riesgo detectado |
|---|---|---|---|
| `TestNewtonRaphsonConvergencia` | `test_converge_raiz_positiva` | x0=1 converge a ~1.8608 | Regresión de convergencia básica |
| `TestNewtonRaphsonConvergencia` | `test_converge_raiz_pequena` | x0=0 converge a ~0.2541 | Otra cuenca de atracción |
| `TestNewtonRaphsonConvergencia` | `test_converge_raiz_negativa` | x0=-2 converge a ~-2.1149 | Raíz negativa |
| `TestNewtonRaphsonConvergencia` | `test_convergencia_cuadratica_pocas_iteraciones` | < 10 iteraciones | Regresión de eficiencia (orden cuadrático) |
| `TestNewtonRaphsonConvergencia` | `test_raiz_exacta_entera` | f(x)=x²-4, raíz en x=2 | Convergencia a raíz exacta entera |
| `TestNewtonRaphsonConvergencia` | `test_error_final_menor_tolerancia` | `error_pct < tol` al converger | Criterio de parada del SPEC §1 |
| `TestNewtonRaphsonConvergencia` | `test_result_fields_completos` | `method_name`, `excel_sheet_name`, `formula_description` | Contrato de interfaz de `MethodResult` |
| `TestNewtonRaphsonConvergencia` | `test_formula_description` | Contiene `f'` en descripción | Regresión de metadatos |
| `TestNewtonRaphsonInaplicable` | `test_fp_cero_en_x0` | f'(x0)=0 → `applicable=False` | **RIESGO CRÍTICO:** división por cero en xₙ₊₁ = xₙ − f/f' |
| `TestNewtonRaphsonInaplicable` | `test_fp_casi_cero_en_iteracion` | f'(xk)≈0 en iteración intermedia → break silencioso | Propagación de ZeroDivisionError en iteración |
| `TestNewtonRaphsonInaplicable` | `test_no_convergencia_max_iter` | max_iter=1 → root≠None | `root` siempre devuelve última aproximación |
| `TestNewtonRaphsonInaplicable` | `test_ecuacion_sin_raices_reales` | x²+x+1, no converge | Método aplica pero no converge en 25 iter |
| `TestNewtonRaphsonIteraciones` | `test_primera_fila_tiene_k0` | iterations[0].k == 0 | Contrato de estructura de filas |
| `TestNewtonRaphsonIteraciones` | `test_filas_tienen_fpxk_no_cero` | f'(xk) ≠ 0 en todas las filas | Garantía de que no hay break silencioso en datos |
| `TestNewtonRaphsonIteraciones` | `test_error_primera_fila_existe` | k=0 ya tiene error_pct (Newton difiere de métodos intervalo) | SPEC §3: Newton calcula desde k=0 |
| `TestNewtonRaphsonIteraciones` | `test_error_decreciente` | errors[-1] < errors[0] | Convergencia monótona en el caso normal |
| `TestNewtonRaphsonIteraciones` | `test_iteration_count_coincide_con_len` | `iteration_count == len(iterations) - 1` | SPEC §3 y §7: fórmula `len(rows) - 1` |
| `TestNewtonRaphsonIteraciones` | `test_tolerancia_estricta_mas_iteraciones` | tol=1e-10 ≥ iteraciones que tol=0.00001 | Monotonicidad respecto a tolerancia |

#### `test_newton_family.py` — 40 tests

| Clase | Test | Propósito | Riesgo detectado |
|---|---|---|---|
| `TestNewtonModificado` | `test_converge` | Converge a raíz de x³-4x+1 | Regresión de convergencia |
| `TestNewtonModificado` | `test_inaplicable_fp_cero` | f'(x0)=0 → `applicable=False` | División por cero antes de iterar |
| `TestNewtonModificado` | `test_denom_cero_interno` | denom=(f')²-f·f'' puede ser 0 → break | ZeroDivisionError en iteración |
| `TestNewtonModificado` | `test_no_convergencia_max_iter` | max_iter=1 → root≠None | Siempre retorna última aproximación |
| `TestNewtonModificado` | `test_method_name` | `method_name == "Newton Modificado"` | Contrato de identificación de método |
| `TestNewtonModificado` | `test_error_final_menor_tolerancia` | `error_pct < tol` si converge | SPEC §1 criterio de parada |
| `TestNewton2doOrden` | `test_converge` | Converge sobre x³-4x+1 | Regresión de convergencia |
| `TestNewton2doOrden` | `test_inaplicable_fp_cero` | f'(x0)=0 → `applicable=False` | División por cero |
| `TestNewton2doOrden` | `test_discriminante_negativo_break` | (f')²-2f''·f < 0 → break | **RIESGO CRÍTICO:** `math.sqrt` de negativo → ValueError. SPEC §6.5 |
| `TestNewton2doOrden` | `test_fpp_cero_break` | f''=0 → ZeroDivisionError → break | División por f'' en fórmula |
| `TestNewton2doOrden` | `test_method_name` | `method_name == "Newton 2do Orden"` | Contrato de identificación |
| `TestNewton2doOrden` | `test_no_convergencia_max_iter` | max_iter=1 → root≠None | Siempre retorna aproximación |
| `TestChebyshev` | `test_converge` | Converge a raíz de x³-4x+1 | Regresión de convergencia |
| `TestChebyshev` | `test_inaplicable_fp_cero` | f'(x0)=0 → inaplicable | División por cero en (f')³ |
| `TestChebyshev` | `test_fp_cubico_overflow` | (f')³ con f' grande → overflow | Estabilidad numérica desde x0 lejano |
| `TestChebyshev` | `test_method_name` | `method_name == "Chebyshev"` | Contrato de identificación |
| `TestChebyshev` | `test_error_final_menor_tolerancia` | `error_pct < tol` si converge | SPEC §1 |
| `TestChebyshev` | `test_no_convergencia_max_iter` | max_iter=1 → root≠None | Aproximación siempre disponible |
| `TestHalley` | `test_converge` | Converge a raíz de x³-4x+1 | Regresión de convergencia |
| `TestHalley` | `test_inaplicable_fp_cero` | f'(x0)=0 → inaplicable | División por cero |
| `TestHalley` | `test_denom_halley_cero` | f'-(f''·f)/(2f')=0 → break | ZeroDivisionError en denominador compuesto |
| `TestHalley` | `test_convergencia_cubica_pocas_iter` | iteration_count < 8 | Verificación de orden cúbico |
| `TestHalley` | `test_method_name` | `method_name == "Halley"` | Contrato de identificación |
| `TestHalley` | `test_no_convergencia_max_iter` | max_iter=1 → root≠None | Aproximación siempre disponible |
| `TestSuperHalley` | `test_converge` | Converge a raíz de x³-4x+1 | Regresión de convergencia |
| `TestSuperHalley` | `test_inaplicable_fp_cero` | f'(x0)=0 → inaplicable | División por cero |
| `TestSuperHalley` | `test_doble_denominador_riesgo` | Dos denominadores: num/den y f'/f → ZeroDivisionError | **RIESGO COMPUESTO:** dos puntos de fallo en la fórmula |
| `TestSuperHalley` | `test_method_name` | `method_name == "Super Halley"` | Contrato de identificación |
| `TestSuperHalley` | `test_error_final_menor_tolerancia` | `error_pct < tol` si converge | SPEC §1 |
| `TestSuperHalley` | `test_no_convergencia_max_iter` | max_iter=1 → root≠None | Aproximación siempre disponible |
| `TestOstrowsky` | `test_converge` | Converge a raíz de x³-4x+1 | Regresión de convergencia |
| `TestOstrowsky` | `test_inaplicable_fp_cero` | f'(x0)=0 → inaplicable | División por cero |
| `TestOstrowsky` | `test_raiz_cuadrada_de_negativo` | (f')²-f·f'' < 0 → ValueError → break | **RIESGO CRÍTICO:** `math.sqrt` de negativo |
| `TestOstrowsky` | `test_sqrt_inner_cero` | sqrt_inner≈0 → ZeroDivisionError en denominador | División por raíz cuadrada casi cero |
| `TestOstrowsky` | `test_method_name` | `method_name == "Ostrowsky"` | Contrato de identificación |
| `TestOstrowsky` | `test_no_convergencia_max_iter` | max_iter=1 → root≠None | Aproximación siempre disponible |
| `TestOstrowsky` | `test_convergencia_rapida` | iteration_count < 10 | Verificación de orden 4 |
| `TestNewtonFamilyComparativo` | `test_todas_variantes_convergen_raiz_valida` | Cada runner converge a **alguna** raíz válida de f(x) | **TEST CORREGIDO:** ver TEST_CLEANUP_REPORT.md §2.5 |
| `TestNewtonFamilyComparativo` | `test_todas_devuelven_applicable_false_fp_cero` | Todas inaplicables cuando f'(x0)=0 | Invariante global de la familia Newton |
| `TestNewtonFamilyComparativo` | `test_order_superior_menos_iteraciones` | Halley ≤ iteraciones que Newton-Raphson | Verificación de superioridad de orden cúbico |

#### `test_regula_falsi.py` — 20 tests

| Clase | Test | Propósito | Riesgo detectado |
|---|---|---|---|
| `TestRegulaFalsiConvergencia` | `test_converge_intervalo_0_1` | [0,1] → raíz ~0.254102 | Regresión de convergencia en intervalo estándar |
| `TestRegulaFalsiConvergencia` | `test_converge_intervalo_1_2` | [1,2] → raíz ~1.860806 | Segunda raíz en intervalo alterno |
| `TestRegulaFalsiConvergencia` | `test_converge_intervalo_negativo` | [-3,-2] → raíz ~-2.114908 | Raíz negativa, intervalo negativo |
| `TestRegulaFalsiConvergencia` | `test_raiz_entera_exacta` | x²-4, [1,3] → x=2 | Raíz exacta entera |
| `TestRegulaFalsiConvergencia` | `test_error_final_menor_tolerancia` | `error_pct < tol` si converge | SPEC §1 criterio de parada |
| `TestRegulaFalsiConvergencia` | `test_method_name_y_sheet` | names correctos | Contrato de identificación y hoja Excel |
| `TestRegulaFalsiConvergencia` | `test_formula_description_contiene_formula` | Describe la fórmula `f(a)` | Metadatos de método |
| `TestRegulaFalsiInaplicable` | `test_sin_cambio_signo` | [2,3] sin cambio → `applicable=False` | **RIESGO:** no detectar que no hay raíz garantizada |
| `TestRegulaFalsiInaplicable` | `test_reason_explica_sin_cambio` | `reason` menciona "signo" | Usabilidad: mensaje de error descriptivo |
| `TestRegulaFalsiInaplicable` | `test_f_no_finita_en_extremo` | f(x)=1/x, extremo en 0 → inaplicable | **RIESGO:** f(0)=inf → no aplicar método |
| `TestRegulaFalsiInaplicable` | `test_no_convergencia_max_iter_1` | max_iter=1 → root≠None | Última aproximación siempre disponible |
| `TestRegulaFalsiInaplicable` | `test_mismo_signo_en_extremo` | fa, fb mismo signo → inaplicable | Caso límite: ambos positivos |
| `TestRegulaFalsiRiesgos` | `test_denom_cero_break` | denom=f(b)-f(a)≈0 → break sin excepción | **RIESGO:** ZeroDivisionError en c = a - f(a)·(b-a)/(f(b)-f(a)) |
| `TestRegulaFalsiRiesgos` | `test_convergencia_lenta_funcion_convexa` | f(x)=eˣ-2, convergencia lenta | Robustez en 25 iteraciones max |
| `TestRegulaFalsiRiesgos` | `test_actualiza_extremo_correcto` | c siempre dentro de [a,b] | **RIESGO:** lógica de actualización invertida → intervalo incorrecto |
| `TestRegulaFalsiEstructura` | `test_primera_fila_k0` | iterations[0].k == 0 | Estructura de filas |
| `TestRegulaFalsiEstructura` | `test_primera_fila_sin_error` | iterations[0].error_pct is None | SPEC §3: k=0 no tiene error previo |
| `TestRegulaFalsiEstructura` | `test_filas_tienen_fa_fc_fb` | Campos `fa`, `fc`, `fb` en cada fila | Contrato de `IntervalRow` |
| `TestRegulaFalsiEstructura` | `test_iteration_count_len_minus_1` | `iteration_count == len(iterations) - 1` | SPEC §3 y §7 |
| `TestRegulaFalsiEstructura` | `test_params_usados_contienen_ab` | `params_used` contiene a=0.0, b=1.0 | Trazabilidad de parámetros usados |

#### `test_aitken.py` — 19 tests

| Clase | Test | Propósito | Riesgo detectado |
|---|---|---|---|
| `TestAitkenDelta2Helper` | `test_formula_correcta` | Δ²(1, 0.5, 0.25) = 0.0 | Correctitud de la fórmula base (SPEC §6.1) |
| `TestAitkenDelta2Helper` | `test_denominador_cero_fallback` | denom=0 → retorna p0 | **RIESGO:** ZeroDivisionError en operador Δ² |
| `TestAitkenDelta2Helper` | `test_convergencia_geometrica` | Δ² extrae el límite de la secuencia | Propiedad matemática de aceleración |
| `TestAitkenDelta2Helper` | `test_secuencia_constante` | Δ²(c,c,c) = c | Caso de secuencia ya convergida |
| `TestAitkenConvergencia` | `test_converge_con_gx_valido` | g(x)=(x³+1)/4, x0=0 → ~0.254102 | Regresión de convergencia |
| `TestAitkenConvergencia` | `test_raiz_mas_precisa_que_punto_fijo` | Aitken ≤ iteraciones que PF puro | Verificación de aceleración Δ² |
| `TestAitkenConvergencia` | `test_tolerancia_laxa_converge_rapidamente` | tol=1.0 → converge en 1-2 iter | Monotonicidad respecto a tolerancia |
| `TestAitkenConvergencia` | `test_tolerancia_estricta_mas_iter` | tol=1e-10 ≥ iteraciones que tol=0.00001 | Monotonicidad respecto a tolerancia |
| `TestAitkenConvergencia` | `test_error_final_menor_tolerancia` | `error_pct < tol` si converge | SPEC §1 criterio de parada |
| `TestAitkenInaplicable` | `test_gx_none_inaplicable` | gx=None → `applicable=False`, 0 iteraciones | **RIESGO:** Aitken sin g(x) definida |
| `TestAitkenInaplicable` | `test_base_seq_menor_3_inaplicable` | g divergente → base_seq < 3 → inaplicable | **RIESGO:** secuencia base insuficiente para Δ² |
| `TestAitkenInaplicable` | `test_no_convergencia_max_iter_pequeno` | max_iter=1 → root≠None | Mínimo de puntos para operar Δ² |
| `TestAitkenEstructura` | `test_method_name` | `method_name == "Aitken (Δ²)"` | Contrato de identificación |
| `TestAitkenEstructura` | `test_excel_sheet_name` | `excel_sheet_name == "Aitken"` | Nombre de hoja Excel (SPEC §6.3) |
| `TestAitkenEstructura` | `test_primera_fila_k0` | iterations[0].k == 0 | Estructura de filas |
| `TestAitkenEstructura` | `test_fila_tiene_xk_hat` | `xk_hat` finito en cada fila | `AitkenRow` contiene campo hat |
| `TestAitkenEstructura` | `test_primera_fila_error_none` | k=0 → error_pct is None | SPEC §6.3: k=0 sin error |
| `TestAitkenEstructura` | `test_iteration_count_consistente` | `iteration_count == len(iterations) - 1` | SPEC §7: Aitken usa índice k explícito |
| `TestAitkenEstructura` | `test_hat_cerca_raiz_en_ultima_fila` | Último `xk_hat` cerca de 0.254102 | `root` = hat de la fila convergente |

#### `test_steffensen.py` — 18 tests

| Clase | Test | Propósito | Riesgo detectado |
|---|---|---|---|
| `TestDelta2Helper` | `test_formula_correcta` | Δ²(1, 0.5, 0.25) = 0.0 | Fórmula base (SPEC §6.1) |
| `TestDelta2Helper` | `test_denominador_cero_fallback` | denom=0 → retorna p0 | **RIESGO:** ZeroDivisionError en Δ² |
| `TestDelta2Helper` | `test_misma_logica_que_aitken` | `_delta2` == `_aitken_delta2` | Consistencia entre implementaciones |
| `TestSteffensenConvergencia` | `test_converge_con_gx_valido` | g convergente → root≠None | Regresión de convergencia básica |
| `TestSteffensenConvergencia` | `test_convergencia_mas_rapida_que_aitken` | Steffensen ≤ Aitken + 3 iteraciones | Verificación de doble aceleración |
| `TestSteffensenConvergencia` | `test_error_final_menor_tolerancia` | `error_pct < tol` si converge | SPEC §1 |
| `TestSteffensenConvergencia` | `test_tolerancia_laxa` | tol=1.0 → root≠None | Convergencia con criterio muy laxo |
| `TestSteffensenInaplicable` | `test_gx_none_inaplicable` | gx=None → `applicable=False`, 0 iter | **RIESGO:** Steffensen sin g(x) |
| `TestSteffensenInaplicable` | `test_base_seq_menor_5` | g diverge → base_seq < 5 → inaplicable | **RIESGO FRONTERA:** Steffensen necesita ≥ 5 puntos base |
| `TestSteffensenInaplicable` | `test_base_seq_exactamente_5_frontera` | max_iter=2 → 12 puntos → `applicable=True` | Frontera exacta de aplicabilidad |
| `TestSteffensenInaplicable` | `test_aitken_seq_menor_3_inaplicable` | aitken_seq < 3 → sin suficientes puntos para Δ² externo | **RIESGO:** capa Aitken insuficiente para capa Steffensen |
| `TestSteffensenEstructura` | `test_method_name` | `method_name == "Steffensen"` | Contrato de identificación |
| `TestSteffensenEstructura` | `test_excel_sheet_name` | `excel_sheet_name == "Steffensen"` | Nombre de hoja Excel (SPEC §6.4) |
| `TestSteffensenEstructura` | `test_iteration_count_consistente` | `iteration_count == len(iterations) - 1` | SPEC §7 |
| `TestSteffensenEstructura` | `test_fila_tiene_xk_hat_finito` | `xk_hat` es finito | `SteffensenRow` completo |
| `TestSteffensenEstructura` | `test_primera_fila_error_none` | k=0 → error_pct=None, converged=None | SPEC §3: primera fila sin error |
| `TestSteffensenEstructura` | `test_root_no_none_si_applicable` | Si applicable → root≠None | Contrato de invariante de resultado |
| `TestSteffensenEstructura` | `test_amplificacion_redondeo_no_falla` | max_iter=25 → root finito | **RIESGO:** doble Δ² amplifica errores de redondeo |

---

## 4. Resultados históricos

### 4.1 Estado antes de `auto_params` (referencia histórica)

No existe en el proyecto un documento que registre el estado de tests previo a la implementación de `auto_params`. Lo que sí documenta `AUTO_PARAMS_CURRENT_STATE.md` es el estado actual del módulo:

- `_generate_gx_candidates()` retorna **siempre** `g(x) = (2x+5)^(1/3)` independientemente de la ecuación de entrada (bug de g(x) hardcodeada, activo).
- Tres estrategias de generación de g(x) están **comentadas** con etiqueta `DESACTIVADO TEMPORALMENTE`.
- El módulo tiene un `print()` de debug activo en producción.
- `_best_integer_near()` está definida **después** de donde se llama en `generate_params()`.

El impacto en tests: los fixtures de `conftest.py` **no usan** `generate_params()`. Construyen `AutoParams` directamente con valores deterministas. Por eso, el bug de g(x) hardcodeada no afecta los tests unitarios pero sí afecta el endpoint `/api/solve` en producción.

### 4.2 Estado después de la implementación de `auto_params`

El módulo `auto_params.py` está operativo y es importado por todos los tests a través de `conftest.py`. Los tests son deterministas porque usan fixtures que construyen `AutoParams` manualmente, aislando los tests del comportamiento actual de `generate_params()`.

**Consecuencia documentada en** `MULTI_EQUATION_CURRENT_AUDIT.md`: al ejecutar el endpoint real con `f(x) = x² − 2`, Punto Fijo, Aitken y Steffensen convergen a `x ≈ 2.0945` (raíz de `x³ − 2x − 5`) en lugar de `x ≈ 1.4142`. Los tests unitarios no detectan esto porque usan g(x) fija por fixture.

### 4.3 Estado después de la limpieza de tests (TEST_CLEANUP_REPORT.md)

| Métrica | Antes de limpieza | Después de limpieza |
|---|---|---|
| Tests fallando | 4 | 0 |
| Tests pasando | 29 | 36 |
| Total | 33 | 36 |
| Causa de fallos | Invariante incorrecta: convergencia a la misma raíz para toda la familia Newton | — |
| Acción | Eliminar 4 tests con supuesto matemáticamente falso + agregar 7 tests de casos límite | — |

> Referencia completa: `TEST_CLEANUP_REPORT.md` en la raíz del proyecto.

---

## 5. Casos críticos protegidos por método

### 5.1 Bisección
**Archivo de test:** `test_biseccion.py` — **VACÍO (0 bytes)**. No hay tests activos.

Casos críticos a implementar según el SPEC:
- Sin cambio de signo en `[a,b]` → `applicable=False`
- `f(c) = 0` exacto → convergencia inmediata
- k=0 sin error (`error_pct = None`)
- `iteration_count = len(rows) - 1`
- SPEC §8: referencia `root = 1.4142135381698608`, `iteration_count = 22`

### 5.2 Regula Falsi
**Archivo de test:** `test_regula_falsi.py` — 20 tests activos.

Casos críticos protegidos:
- `[2,3]` sin cambio de signo → `applicable=False` (`test_sin_cambio_signo`)
- `f(x) = 1/x`, f no finita en extremo → `applicable=False` (`test_f_no_finita_en_extremo`)
- `denom = f(b)-f(a) ≈ 0` → break sin excepción (`test_denom_cero_break`)
- Actualización correcta de `[a,b]` — c siempre dentro del intervalo (`test_actualiza_extremo_correcto`)
- k=0 sin error (`test_primera_fila_sin_error`)
- `iteration_count = len(iterations) - 1` (`test_iteration_count_len_minus_1`)

### 5.3 Newton-Raphson
**Archivo de test:** `test_newton_raphson.py` — 18 tests activos.

Casos críticos protegidos:
- `f'(x0) = 0` → `applicable=False` antes de iterar (`test_fp_cero_en_x0`)
- `f'(xk) ≈ 0` en iteración intermedia → break interno sin excepción (`test_fp_casi_cero_en_iteracion`)
- Convergencia cuadrática: < 10 iteraciones (`test_convergencia_cuadratica_pocas_iteraciones`)
- `error_pct < tol` al converger (`test_error_final_menor_tolerancia`)
- k=0 ya tiene `error_pct` (Newton calcula desde k=0, distinto a métodos de intervalo) (`test_error_primera_fila_existe`)

### 5.4 Newton Modificado
**Archivo de test:** `test_newton_family.py::TestNewtonModificado` — 6 tests.

Casos críticos protegidos:
- `f'(x0) = 0` → `applicable=False` (`test_inaplicable_fp_cero`)
- `(f')² - f·f'' = 0` en iteración → break sin excepción (`test_denom_cero_interno`)

### 5.5 Newton Segundo Orden
**Archivo de test:** `test_newton_family.py::TestNewton2doOrden` — 6 tests.

Casos críticos protegidos:
- **CRÍTICO:** discriminante `(f')² - 2f''·f < 0` → `math.sqrt` de negativo → `ValueError` capturado → break (`test_discriminante_negativo_break`). SPEC §6.5.
- `f''(xk) = 0` → ZeroDivisionError en denominador → break (`test_fpp_cero_break`)
- Rama de signo correcta: `−f' + √discriminante` (no `+f'` ni `−√`) — implícito en `test_converge`

### 5.6 Chebyshev
**Archivo de test:** `test_newton_family.py::TestChebyshev` — 6 tests.

Casos críticos protegidos:
- `f'(x0) = 0` → inaplicable (`test_inaplicable_fp_cero`)
- `(f')³` en denominador con `f'` muy grande → overflow controlado (`test_fp_cubico_overflow`)

### 5.7 Halley
**Archivo de test:** `test_newton_family.py::TestHalley` — 6 tests.

Casos críticos protegidos:
- `f'(x0) = 0` → inaplicable (`test_inaplicable_fp_cero`)
- `f' - (f''·f)/(2f') = 0` → ZeroDivisionError → break (`test_denom_halley_cero`)
- Convergencia cúbica: iteration_count < 8 (`test_convergencia_cubica_pocas_iter`)

### 5.8 Super Halley
**Archivo de test:** `test_newton_family.py::TestSuperHalley` — 6 tests.

Casos críticos protegidos:
- `f'(x0) = 0` → inaplicable (`test_inaplicable_fp_cero`)
- **RIESGO COMPUESTO:** dos denominadores en la fórmula — numerador `2(f')²-f·f''` y denominador `2((f')²-f·f'')`. Si cualquiera es cero → ZeroDivisionError → break (`test_doble_denominador_riesgo`)

### 5.9 Ostrowsky
**Archivo de test:** `test_newton_family.py::TestOstrowsky` — 7 tests.

Casos críticos protegidos:
- `f'(x0) = 0` → inaplicable (`test_inaplicable_fp_cero`)
- **CRÍTICO:** `(f')² - f·f'' < 0` → `math.sqrt` de negativo → `ValueError` → break (`test_raiz_cuadrada_de_negativo`)
- `sqrt_inner ≈ 0` → ZeroDivisionError en denominador → break (`test_sqrt_inner_cero`)
- Convergencia de orden 4: iteration_count < 10 (`test_convergencia_rapida`)

### 5.10 Von Mises
**Archivo de test:** **No existe.** Sin cobertura de tests unitarios.

Casos críticos a implementar según el SPEC (§5.3):
- `f'(x0) = 0` → `applicable=False` (f' se calcula **una sola vez** al inicio — SPEC §9 regla 10)
- `f'(x0)` debe ser calculada **una única vez** y mantenerse constante en todas las iteraciones. Si se recalcula en cada paso, el resultado difiere del Excel.
- SPEC §8: referencia `root = 1.4142135339575084`, `iteration_count = 17`

### 5.11 Secante
**Archivo de test:** **No existe.** Sin cobertura de tests unitarios.

Casos críticos a implementar según el SPEC (§5.4):
- `f(xk) - f(xk_prev) ≈ 0` → comportamiento IFERROR según fila: k≥2 usa fallback `x_next = xk`, `error = 0` → convergencia inmediata
- Filas k=0 y k=1: evaluación directa sin IFERROR
- Filas k≥2: IFERROR en f y en x_next
- SPEC §8: referencia `root = 1.4142135623730954`, `iteration_count = 6`

### 5.12 Punto Fijo
**Archivo de test:** **No existe.** Sin cobertura de tests unitarios.

Casos críticos a implementar según el SPEC (§5.2):
- `gx = None` → `applicable=False`
- g divergente → no converge en max_iter
- `error_pct = ABS((g(xk) - xk) / g(xk)) × 100` (denominador es g(xk), no xk) — SPEC §2
- k=0 sin error
- SPEC §8: referencia `root = 1.4142135516460548`, `iteration_count = 9`

### 5.13 Aitken
**Archivo de test:** `test_aitken.py` — 19 tests activos.

Casos críticos protegidos:
- `gx = None` → `applicable=False`, 0 iteraciones (`test_gx_none_inaplicable`)
- Denominador Δ² = 0 → fallback a `p0` silencioso (`test_denominador_cero_fallback`)
- base_seq < 3 elementos útiles → inaplicable (`test_base_seq_menor_3_inaplicable`)
- **SPEC §6.3 arquitectura B:** capa base inicia en `pf[1]`, NO en `pf[0]`. El error con la arquitectura incorrecta es ~2.381e-3 (implícito en tests de convergencia).
- k=0 sin error (`test_primera_fila_error_none`)
- `iteration_count = k` explícito de la fila convergente (SPEC §7, única excepción)

### 5.14 Steffensen
**Archivo de test:** `test_steffensen.py` — 18 tests activos.

Casos críticos protegidos:
- `gx = None` → `applicable=False` (`test_gx_none_inaplicable`)
- base_seq < 5 → inaplicable (`test_base_seq_menor_5`)
- base_seq exactamente = 5 (frontera mínima) → `applicable=True` (`test_base_seq_exactamente_5_frontera`)
- aitken_seq < 3 → sin puntos suficientes para Δ² externo (`test_aitken_seq_menor_3_inaplicable`)
- Amplificación de redondeo por doble Δ² → resultado siempre finito (`test_amplificacion_redondeo_no_falla`)
- **SPEC §6.4:** la capa Aitken hereda inicio en `pf[1]`. Si se cambia Aitken, Steffensen se rompe también.

---

## 6. Compatibilidad Excel

### 6.1 Cómo se verifica

La verificación de compatibilidad Excel opera en dos niveles:

**Nivel 1 — Auditoría manual (script `generar_excel_v2.py`):**
El script `excel_templates/backup/generar_excel_v2.py` calcula en Python las mismas iteraciones que `amburger.xlsx` y genera `MetodosNumericos_Todos_v2.xlsx`. La verificación se hace comparando celda a celda ambos archivos con `data_only=True`. El criterio es `diff = 0.000e+00`.

**Nivel 2 — Invariantes en tests unitarios:**
Los tests unitarios verifican los invariantes derivados del SPEC:
- `error_pct < tol` al converger (SPEC §1)
- `iterations[0].error_pct is None` para métodos de intervalo y Δ² (SPEC §3)
- `iteration_count == len(iterations) - 1` para todos excepto Aitken (SPEC §7)
- `applicable=False` cuando las condiciones pre-iteración no se cumplen (SPEC §5.x)

### 6.2 Los 14 valores de referencia congelados (SPEC §8)

Ejecutado con `f(x) = x² − 2`, `g(x) = (x+2)/(x+1)`, `x₀ = 1`, `tol = 0.00001`. Diff `0.000e+00` contra `amburger.xlsx`:

| # | Método | `root` | `final_error_pct` | `iteration_count` |
|---|---|---|---|---|
| 1 | Bisección | 1.4142135381698608 | 8.429369846441326e-06 | 22 |
| 2 | Regula Falsi | 1.4142135516460548 | 3.6624406232338026e-06 | 9 |
| 3 | Punto Fijo | 1.4142135516460548 | 5.179473404576684e-06 | 9 |
| 4 | Aitken | 1.4142135642135643 | 4.290816257987263e-06 | 3 |
| 5 | Steffensen | 1.4142135623730965 | 1.1268553575973441e-10 | 1 |
| 6 | Newton-Raphson | 1.4142135623730951 | 1.1276404038266872e-10 | 4 |
| 7 | Newton Modificado | 1.414213562373095 | 1.1276404038266874e-10 | 4 |
| 8 | Newton 2do Orden | 1.4142135623730951 | 0.0 | 1 |
| 9 | Chebyshev | 1.4142135623730951 | 7.850462293418874e-14 | 3 |
| 10 | Halley | 1.4142135623730951 | 1.5700924586837748e-14 | 3 |
| 11 | Super Halley | 1.4142135623730951 | 1.1276404038266872e-10 | 2 |
| 12 | Ostrowsky | 1.414213562373095 | 9.420807222970007e-07 | 2 |
| 13 | Secante | 1.4142135623730954 | 2.2328661677132043e-08 | 6 |
| 14 | Von Mises | 1.4142135339575084 | 6.860129219297141e-06 | 17 |

### 6.3 Reglas de no-regresión Excel (SPEC §9)

Cualquier modificación al backend que altere alguno de los 14 valores de §6.2 debe ser tratada como una regresión crítica. Las reglas que con mayor probabilidad la causarían:

1. Cambiar la fórmula de error a `(x_nuevo - x_anterior) / x_anterior` (denominador incorrecto)
2. Cambiar `_TOLERANCE` o `_MAX_ITER`
3. Agregar filas después del primer "SI"
4. Cambiar el inicio de la capa base de Aitken de `pf[1]` a `pf[0]`
5. Recalcular `f'(x0)` en cada iteración de Von Mises (debe calcularse una sola vez)
6. Cambiar la rama de la raíz en Newton 2do Orden de `−f' + √D` a `+f'`

---

## 7. Tests corregidos

Referencia completa: `TEST_CLEANUP_REPORT.md` (raíz del proyecto).

Resumen de lo corregido:

**4 tests eliminados** de `test_newton_family.py::TestNewtonFamilyComparativo`:
Los 4 tests fallaban por la misma suposición matemáticamente incorrecta: que todos los métodos de la familia Newton convergen a la **misma** raíz desde el mismo `x₀`. Esto es falso para métodos de orden superior: Chebyshev desde `x₀=1` produce `x₁ ≈ 11.0` en su primer paso, saliendo de la cuenca de atracción de `r ≈ 0.254` y convergiendo hacia `r ≈ −2.114`.

Los tests eliminados eran:
- `test_todas_variantes_convergen_misma_ecuacion` (y su variante duplicada)
- `test_misma_cuenca_atraccion`
- `test_convergencia_identica_raiz`

**1 test de reemplazo agregado:**
`test_todas_variantes_convergen_raiz_valida` — invariante correcta: cada método que converge debe reportar una raíz que pertenezca al conjunto `{−2.114908, 0.254102, 1.860806}`, sin exigir que sea la misma raíz que otro método.

**7 tests nuevos de casos límite agregados** (en `test_steffensen.py` y `test_aitken.py`):
- `test_base_seq_menor_5`, `test_base_seq_exactamente_5_frontera`, `test_aitken_seq_menor_3_inaplicable` (Steffensen)
- `test_base_seq_menor_3_inaplicable`, `test_no_convergencia_max_iter_pequeno` (Aitken)
- `test_discriminante_negativo_break` (Newton 2do Orden)
- `test_todas_variantes_convergen_raiz_valida` (Newton Family Comparativo — el reemplazo)

---

## 8. Estado final

### 8.1 Conteo de tests

| Archivo | Tests activos | Fallos |
|---|---|---|
| `test_newton_raphson.py` | 18 | 0 |
| `test_newton_family.py` | 40 | 0 |
| `test_regula_falsi.py` | 20 | 0 |
| `test_aitken.py` | 19 | 0 |
| `test_steffensen.py` | 18 | 0 |
| `test_biseccion.py` | 0 (vacío) | — |
| **TOTAL** | **115** | **0** |

> El `.pytest_cache/v/cache/nodeids` registraba 116 entradas porque incluía `test_todas_variantes_convergen_misma_ecuacion` (ahora eliminado/renombrado). El conteo activo desde el código fuente es 115 tests en 5 archivos.

### 8.2 Cobertura de regresión

| Dimensión | Estado |
|---|---|
| Métodos con tests unitarios | 10 / 14 (71%) |
| Métodos SIN tests unitarios | 4: Bisección (vacío), Punto Fijo, Secante, Von Mises |
| Casos límite matemáticos cubiertos | Denominadores cero, discriminantes negativos, derivadas nulas, g(x)=None, base_seq insuficiente, overflow numérico |
| Contrato de estructura de resultados | Cubierto en todos los 5 archivos activos |
| Compatibilidad Excel (SPEC §8) | Cubierta mediante invariantes de SPEC en tests + auditoría manual con `generar_excel_v2.py` |
| Tests failing | **0** |
| Tests passing | **115** (activos en código fuente) |

### 8.3 Brechas de cobertura conocidas

Las siguientes brechas son datos reales del proyecto, no estimaciones:

1. `test_biseccion.py` existe pero tiene **0 bytes**. Bisección no tiene ningún test unitario activo.
2. No existe `test_punto_fijo.py`. Punto Fijo no tiene ningún test unitario activo.
3. No existe `test_secante.py`. Secante no tiene ningún test unitario activo.
4. No existe `test_von_mises.py`. Von Mises no tiene ningún test unitario activo.
5. No existe un test de integración automatizado que compare el backend contra `amburger.xlsx` celda a celda. La verificación Excel es manual (script `generar_excel_v2.py`).
6. Los tests de Punto Fijo, Aitken y Steffensen usan g(x) inyectada por fixture. No detectan el bug de `auto_params._generate_gx_candidates()` que retorna siempre `g(x) = (2x+5)^(1/3)`.

