# RESIDUAL_METHODS_AUDIT.md

> Auditoría de casos residuales sobre los 4 métodos solicitados  
> **Versión:** 2 — post-parche Steffensen  
> **Fecha:** 2026-06-06  
> Código fuente: `metodos_numericos_web.zip` (backend/, docs/)  
> Ejecutado en Python 3 con sympy + numpy  
> **Sin modificar fórmulas matemáticas. Sin tocar Excel compatibility.**

---

## Metodología

Cada método se ejecutó sobre las 6 ecuaciones con parámetros generados automáticamente por `generate_params()`.  
Los casos catalogados como residuales son aquellos donde el método:

- reporta `converged=False` con raíz incorrecta (divergencia real), o
- reporta `converged=False` con raíz correcta (fallo de detección), o
- oscila sin alcanzar tolerancia en 25 iteraciones.

Los casos donde `applicable=False` por `f'(x₀)=0` **no son residuales**: son comportamientos correctos del pre-chequeo ya documentados en la auditoría anterior.

---

## Tabla resumen: estado actual de los 4 métodos

| Ecuación | x0 auto | Von Mises | Newton 2do Orden | Ostrowsky | Steffensen |
|----------|---------|-----------|------------------|-----------|------------|
| x²−2 | −1.0 | ✅ 17 iter | ✅ 1 iter | ✅ 5 iter | ✅ 1 iter |
| x³−2x−5 | 2.0 | ✅ 6 iter | ✅ 2 iter | ✅ 2 iter | ✅ 1 iter ✅ **CORREGIDO** |
| x³−x−1 | 1.0 | **⚠️ 24 iter** | ✅ 3 iter | ✅ 2 iter | ✅ 1 iter |
| cos(x)−x | 1.0 | ✅ 6 iter | **⚠️ 5 iter** | **⚠️ 5 iter** | ✅ 1 iter |
| e^−x−x | 1.0 | ✅ 8 iter | **⚠️ 1 iter** | **⚠️ 25 iter** | ✅ 1 iter ✅ **CORREGIDO** |
| x⁴−10 | −2.0 | ✅ 11 iter | ✅ 6 iter | **⚠️ 25 iter** | ✅ 1 iter |

**Leyenda:** ✅ converged=True, raíz correcta | ⚠️ converged=False (ver detalle)

**Casos residuales confirmados post-parche: 6** (los 2 de Steffensen fueron corregidos)  
**Casos residuales originales: 8** (6 limitaciones + 2 bugs de Steffensen → ambos bugs resueltos)

---

## Cambios respecto a la versión anterior

### Steffensen — Bug corregido

**Los 2 casos clasificados como "Bug de implementación" en la versión 1 han sido corregidos.**

#### Parche aplicado

Archivo: `backend/methods/steffensen.py`  
Tipo de cambio: **adición de bloque de fallback únicamente** — no se modificó ninguna fórmula matemática, ninguna lógica de capa PF/Aitken/Steffensen, ni ningún valor de referencia Excel.

**Diff exacto (línea 209 del original):**

```diff
+    # ── Fallback: 1 sola fila Steffensen y aún no convergió ──────────────────
+    # Ocurre cuando gx converge cuadráticamente (Newton-like): la capa PF llega
+    # a la raíz en 3-4 pasos → aitken_seq produce exactamente 3 valores →
+    # el loop ejecuta solo k=0 → prev_stef=None → el comparador nunca dispara,
+    # aunque la raíz calculada en k=0 ya es exacta.
+    # Criterio alternativo mínimo: |f(stef_k0)| < tol
+    # No toca la lógica de ≥2 filas ni la compatibilidad Excel.
+    if not converged and len(rows) == 1 and root is not None:
+        try:
+            f_at_root = abs(float(eq.f_sympy.subs(_x, root).evalf()))
+            if f_at_root < tol:
+                converged = True
+                final_error = f_at_root  # reportamos |f(raíz)| como error final
+                rows[0] = SteffensenRow(
+                    k=rows[0].k,
+                    p0=rows[0].p0,
+                    p1=rows[0].p1,
+                    p2=rows[0].p2,
+                    xk_hat=rows[0].xk_hat,
+                    x_new=rows[0].x_new,
+                    error_pct=final_error,
+                    converged=True,
+                )
+        except Exception:
+            pass  # si falla la evaluación, dejamos converged=False sin cambio
```

**Condición de activación del fallback:**
- `len(rows) == 1` — exactamente 1 fila Steffensen producida
- `not converged` — el comparador normal no disparó (porque k=0 no tiene `prev_stef`)
- `|f(stef_k0)| < tol` — la raíz ya satisface el criterio de convergencia funcional

**Condiciones en que el fallback NO activa:**
- Cuando hay ≥2 filas Steffensen (el caso normal, incluyendo Excel x²−2)
- Cuando `len(rows) == 1` pero `|f(stef)| ≥ tol` (raíz no válida → se mantiene `converged=False`)
- Cualquier excepción en la evaluación de `f` → se captura silenciosamente

**Resultados post-parche verificados:**

| Ecuación | gx | stef_k0 | \|f(stef)\| | converged |
|----------|-----|---------|-------------|-----------|
| x³−2x−5, x0=2.0 | (2x³+5)/(3x²−2) | 2.0945514815423265 | 3.64e-12 | **True** |
| e^−x−x, x0=1.0 | (x+1)/(eˣ+1) | 0.5671432904097838 | 3.39e-13 | **True** |

**Tests post-parche:** 25/25 PASS (suite completa de `test_steffensen.py` ejecutada manualmente)  
**Excel 14/14:** Steffensen PASS (root_diff=0.000e+00, err_diff=0.000e+00, iter=1/1 ✅)

---

## 1. Von Mises

### Caso residual: `x³−x−1` — OSCILACIÓN

**Ecuación:** x³−x−1  
**Parámetros:** x0=1.0, f'(x0)=2.0 (constante Von Mises), tol=0.00001, max_iter=25  
**Raíz real:** 1.32471795724...  
**Resultado:** converged=False, 24 iteraciones, raíz reportada=1.4897888178, error final=27.41%

#### Iteraciones observadas

```
k=0:  xk=1.000000 → x_next=1.500000  (err=33.33%)
k=1:  xk=1.500000 → x_next=1.062500  (err=41.18%)
k=2:  xk=1.062500 → x_next=1.494019  (err=28.88%)
k=3:  xk=1.494019 → x_next=1.073635  (err=39.16%)
...   oscila entre ≈1.08 y ≈1.49 indefinidamente
k=22: xk=1.081406 → x_next=1.489790
k=23: xk=1.489790 → x_next=1.081410
k=24: xk=1.081410 → x_next=1.489789
```

#### Causa matemática exacta

Von Mises usa la fórmula `xₙ₊₁ = xₙ − f(xₙ)/f'(x₀)` con **f'(x₀) fijo** para todas las iteraciones. La convergencia requiere que el factor de contracción sea menor que 1:

```
|1 − f'(xₙ)/f'(x₀)| < 1  para todo xₙ en la trayectoria
```

Para `x³−x−1` con x0=1:
- f'(x) = 3x²−1
- f'(x0) = f'(1) = 2.0 (congelado)
- En la raíz α≈1.3247: f'(α) = 3(1.3247)²−1 ≈ 4.268
- Factor local: |1 − 4.268/2.0| = 1.134 **> 1** → contracción imposible

#### Clasificación

**Limitación inherente del método.** No hay error de implementación.

---

## 2. Newton 2do Orden

### Casos residuales: `cos(x)−x` y `e^−x−x` — DIVERGENCIA POR SIGNO DE DISCRIMINANTE

#### Formulación implementada

```
xₙ₊₁ = xₙ + (−f'(xₙ) + √((f'(xₙ))² − 2·f''(xₙ)·f(xₙ))) / f''(xₙ)
```

La raíz cuadrada se evalúa sobre `D = (f')² − 2·f''·f`. Si `D < 0`, el método lanza `ValueError` y se detiene.

---

#### Caso 2a: `cos(x)−x`, x0=1.0

**Raíz real:** 0.7390851332...  
**Resultado:** converged=False, 5 iteraciones, raíz reportada=−47.9617, error=22.16%

**Causa:** La implementación usa siempre `+√D` sin verificar cuál signo minimiza el paso. En `cos(x)−x` desde x0=1, esto produce el paso hacia la raíz alejada, generando una secuencia monótonamente divergente.

#### Caso 2b: `e^−x−x`, x0=1.0

**Raíz real:** 0.5671432904...  
**Resultado:** converged=False, 1 iteración, raíz reportada=14293.916, error=99.94%

**Causa:** El primer paso salta a x≈8.87. Desde ahí, f''=e^−x≈0.00014, produciendo un paso de magnitud ≈14285.

#### Clasificación

**Problema de implementación (parcial) + limitación inherente.** La elección fija de `+√D` sin criterio de mínimo paso causa divergencia desde x0=1 para estas funciones. Sin embargo, incluso con elección óptima de signo, Newton 2do Orden puede divergir por el mal condicionamiento local. **No se corrige en este parche** — el EXCEL_COMPATIBILITY_SPEC.md §6.5 especifica explícitamente la rama `+√D` para compatibilidad con amburger.xlsx. Cambiar la elección de signo rompería la compatibilidad Excel.

---

## 3. Ostrowsky

### Formulación implementada

```
xₙ₊₁ = xₙ − f(xₙ) / √((f'(xₙ))² − f(xₙ)·f''(xₙ))
```

### Casos residuales

#### Caso 3a: `cos(x)−x`, x0=1.0

**Resultado:** converged=False, 5 iteraciones, diverge a ≈12.4  
**Causa:** Para `cos(x)−x` desde x0=1, `f·f''` tienen el mismo signo → `inner < (f')²` → el paso es mayor que Newton-Raphson → la iteración escapa hacia valores grandes.

#### Caso 3b: `e^−x−x`, x0=1.0

**Resultado:** converged=False, 25 iteraciones, diverge a ≈34,299,972  
**Causa:** Para x grande, f''=e^−x→0, haciendo `inner→(f')²≈1` y el paso efectivo ≈ −f ≈ x → duplicación geométrica `xₙ₊₁ ≈ 2xₙ`.

#### Caso 3c: `x⁴−10`, x0=−2.0

**Resultado:** converged=False, 25 iteraciones, diverge a ≈−36,727  
**Causa:** Para `x⁴−10` con x negativo grande, `inner = 4x⁶` → paso ≈ x/2 → razón de crecimiento 3/2.

#### Clasificación

**Limitación inherente del método.** Ostrowsky tiene una cuenca de convergencia estricta. Para funciones oscilatorias y exponenciales decrecientes, el basin of attraction puede no incluir x0=1. No hay error de implementación.

---

## 4. Steffensen — CORREGIDO

### Diagnóstico original

Los 2 casos de `x³−2x−5` y `e^−x−x` eran **bugs de implementación** (lógica de convergencia), no limitaciones matemáticas:

- La raíz calculada era **correcta**
- El problema era que `converged=False` aunque la raíz ya satisfacía la condición

### Causa raíz (confirmada independientemente)

Cuando gx converge cuadráticamente (Newton-like), la secuencia PF alcanza la precisión de float64 en 3-4 pasos. Esto hace que:
1. `aitken_seq` produzca exactamente 3 valores (denominador Δ²→0 en paso 4)
2. El loop Steffensen ejecute `range(3-2) = range(1)` → solo k=0
3. En k=0: `prev_stef=None` → `error_pct=None` → `converged` nunca se activa
4. `converged=False` aunque `stef_k0` es la raíz exacta

### Solución aplicada

Bloque de fallback post-loop que evalúa `|f(stef_k0)| < tol` solo cuando `len(rows)==1` y `not converged`. El fallback **no activa** para el caso normal (≥2 filas Steffensen, incluyendo todos los casos Excel).

### Resultados verificados

| Ecuación | Antes | Después |
|----------|-------|---------|
| x³−2x−5, x0=2.0 | converged=False, error=None | **converged=True**, \|f(raíz)\|=3.6e-12 |
| e^−x−x, x0=1.0 | converged=False, error=None | **converged=True**, \|f(raíz)\|=3.4e-13 |
| x²−2, x0=1.0 (Excel) | converged=True (sin cambio) | **converged=True** (sin cambio) |

---

## Resumen clasificado por tipo de fallo

| Método | Ecuación(es) | Tipo | Descripción resumida | Estado |
|--------|-------------|------|----------------------|--------|
| Von Mises | x³−x−1 | **Limitación inherente** | f'(x0)≪f'(α): factor de contracción >1, oscilación permanente | Sin cambio |
| Newton 2do Orden | cos(x)−x | **Impl. parcial + limitación** | Elección fija +√D sin criterio de mínimo paso; diverge desde cuenca incorrecta | Sin cambio (Excel-locked) |
| Newton 2do Orden | e^−x−x | **Limitación + impl. parcial** | Primer paso produce x≫α; f''→0 hace denominador≈0 en k=1 | Sin cambio (Excel-locked) |
| Ostrowsky | cos(x)−x | **Limitación inherente** | inner>(f')²·(1−ε) desde x0=1; amplificación del paso, divergencia oscilante | Sin cambio |
| Ostrowsky | e^−x−x | **Limitación inherente** | f''→0 → inner→(f')²≈1 → paso≈−f≈x → duplicación geométrica | Sin cambio |
| Ostrowsky | x⁴−10 | **Limitación inherente** | inner=4x⁶ → paso≈x·(1/2) → razón de crecimiento 3/2 | Sin cambio |
| Steffensen | x³−2x−5 | ~~Bug de implementación~~ | gx Newton-like: 3 valores Aitken → 1 fila Steffensen → comparador no disparaba | **✅ CORREGIDO** |
| Steffensen | e^−x−x | ~~Bug de implementación~~ | Mismo patrón: gx rápido → 3 valores Aitken → raíz correcta sin converged=True | **✅ CORREGIDO** |

---

## Estado final de la suite

| Métrica | Valor |
|---------|-------|
| Tests Steffensen (manual) | **25/25 PASS** |
| Excel Steffensen (x²−2) | **PASS** (diff=0.000e+00) |
| Bisección iteration_count | off-by-1 (pre-existente, sin cambio) |
| Regula Falsi iteration_count | off-by-1 (pre-existente, sin cambio) |
| Archivos modificados | `backend/methods/steffensen.py` (únicamente) |
| Líneas añadidas | 25 |
| Líneas eliminadas | 0 |
| Fórmulas matemáticas modificadas | **0** |
