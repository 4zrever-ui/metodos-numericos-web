# EXCEL_COMPATIBILITY_SPEC.md

**Documento de referencia de compatibilidad con amburger.xlsx**
Estado: CONGELADO — 14/14 métodos validados
Fecha de congelación: 2026-06-06
Auditoría ejecutada con: `f(x) = x² − 2`, `g(x) = (x+2)/(x+1)`, `x0 = 1`, `tol = 0.00001`

---

## 1. Parámetros globales

Estos valores están hardcodeados en cada hoja de amburger.xlsx y deben mantenerse idénticos en el backend. No son configurables por el usuario sin romper la compatibilidad.

| Parámetro | Valor | Constante en código |
|---|---|---|
| Tolerancia | `0.00001` | `_TOLERANCE = 0.00001` |
| Máximo de iteraciones | `25` | `_MAX_ITER = 25` |
| Fórmula de error % | `ABS((nuevo − anterior) / nuevo) × 100` | ver §2 |
| Criterio de convergencia | `error_pct < 0.00001` | `conv = error_pct < tol` |
| Criterio de detención | Primer "SI" — el método para inmediatamente | ver §3 |

---

## 2. Fórmula de error porcentual

Excel usa esta fórmula en todos los métodos sin excepción:

```
Error% = ABS( (x_nuevo − x_anterior) / x_nuevo ) × 100
```

En código Python:

```python
if abs(x_nuevo) > 1e-15:
    error_pct = abs((x_nuevo - x_anterior) / x_nuevo) * 100
else:
    error_pct = abs(x_nuevo - x_anterior) * 100
```

La segunda rama (cuando `x_nuevo ≈ 0`) evita división por cero y no tiene equivalente explícito en Excel porque Excel muestra `#DIV/0!` en ese caso — lo que equivale a detener el cálculo.

**La fórmula de error NO es:**
- `ABS((nuevo − anterior) / anterior) × 100` ← incorrecto
- `ABS(nuevo − anterior)` ← incorrecto
- `ABS(f(nuevo))` ← incorrecto

---

## 3. Criterio de detención y `iteration_count`

Excel evalúa en cada fila: `=IF(error_pct < 0.00001, "SI", "NO")`.

Reglas derivadas de esa lógica:

**Fila k=0:** nunca tiene error (no hay fila anterior). La columna de error queda vacía en Excel. El backend devuelve `error_pct = None` y `converged = None` para esa fila.

**Fila k=1 en adelante:** se calcula el error. Si es "SI", el método para ahí mismo y no genera más filas.

**`iteration_count`** es siempre el índice `k` de la última fila generada (la fila donde aparece el primer "SI", o la última fila si no converge):

```python
iteration_count = len(rows) - 1
```

Esta regla aplica a todos los métodos excepto Aitken (ver §6.4).

---

## 4. `root` — definición

`root` es el valor `x_nuevo` de la última fila generada (la fila donde ocurre el primer "SI"). No es el valor `xk` de esa fila, sino el valor calculado (`x_next`, `c`, `gxk`, `hat`, etc.).

---

## 5. Arquitectura por grupo de métodos

### 5.1 Métodos de intervalo — Bisección y Regula Falsi

Parámetros de entrada: `a`, `b` (extremos del intervalo).

**Bisección:**
```
c = (a + b) / 2
```
- k=0: no hay error (primera fila).
- k≥1: `error_pct = ABS((c_k − c_{k-1}) / c_k) × 100`.
- Actualización del intervalo: si `f(a)·f(c) < 0` → `b = c`, si no → `a = c`.
- `root = c` de la fila convergente.

**Regula Falsi:**
```
c = a − f(a) · (b − a) / (f(b) − f(a))
```
- Misma lógica de error e `iteration_count` que Bisección.
- Actualización: si `f(a)·f(c) < 0` → `b = c`, si no → `a = c`.

---

### 5.2 Métodos de punto fijo — Punto Fijo

Parámetros de entrada: `x0`, `g(x)` (función de iteración).

```
xk_new = g(xk)
```

- k=0: `xk = x0`, `gxk = g(x0)`. Sin error.
- k≥1: `error_pct = ABS((g(xk) − xk) / g(xk)) × 100`.
- `root = g(xk)` de la fila convergente.
- `iteration_count = len(rows) - 1`.

---

### 5.3 Familia Newton — Newton-Raphson, Newton Modificado, Chebyshev, Halley, Super Halley, Ostrowsky, Von Mises

Parámetros de entrada: `x0`.

Estructura general:
- Cada fila k evalúa `f(xk)`, `f'(xk)` y opcionalmente `f''(xk)`.
- Calcula `x_next` con la fórmula del método.
- `error_pct = ABS((x_next − xk) / x_next) × 100`.
- `root = x_next` de la fila convergente.
- `iteration_count = len(rows) - 1`.

Fórmulas de cada método:

| Método | Fórmula de iteración |
|---|---|
| Newton-Raphson | `xₙ₊₁ = xₙ − f / f'` |
| Newton Modificado | `xₙ₊₁ = xₙ − (f·f') / ((f')²−f·f'')` |
| Newton 2do Orden | `xₙ₊₁ = xₙ + (−f' + √((f')²−2f''·f)) / f''` |
| Chebyshev | `xₙ₊₁ = xₙ − f/f' − (f²·f'') / (2·(f')³)` |
| Halley | `xₙ₊₁ = xₙ − f / (f' − (f''·f)/(2·f'))` |
| Super Halley | `xₙ₊₁ = xₙ − (2(f')²−f·f'') / (2((f')²−f·f'')) · (f/f')` |
| Ostrowsky | `xₙ₊₁ = xₙ − (f'/√((f')²−f·f'')) · (f/f')` |
| Von Mises | `xₙ₊₁ = xₙ − f(xₙ) / f'(x₀)` ← **f'(x₀) fija, calculada una sola vez** |

**Von Mises — caso especial:** `f'(x₀)` se calcula una única vez al inicio y se mantiene constante en todas las iteraciones. No se recalcula en cada paso.

---

### 5.4 Secante

Parámetros de entrada: `x0`, `x1` (dos puntos iniciales distintos).

```
xₙ₊₁ = xₙ − f(xₙ) · (xₙ − xₙ₋₁) / (f(xₙ) − f(xₙ₋₁))
```

La hoja Excel tiene un comportamiento IFERROR que varía por fila:

| Fila | Columna C (f(x)) | Columna F (x_next) | Columna G (error) |
|---|---|---|---|
| k=0 | sin IFERROR | vacía | vacía |
| k=1 | sin IFERROR | sin IFERROR — si falla, `#DIV/0!` visible | `IFERROR(..., 0)` |
| k≥2 | `IFERROR(..., 0)` | `IFERROR(..., xk)` | `IFERROR(..., 0)` |

Consecuencia para k≥2: si el denominador `f(xk) − f(xk_prev) ≈ 0`, Excel hace fallback a `x_next = xk`, `error = 0`, y como `0 < 0.00001` el método converge. El backend replica este comportamiento.

`iteration_count = len(rows) - 1` (fila k=0 no tiene error).

---

## 6. Métodos especiales — arquitecturas con capas

### 6.1 Operador Δ² (base de Aitken y Steffensen)

```
Δ²(p0, p1, p2) = p0 − (p1 − p0)² / (p2 − 2·p1 + p0)
```

Si el denominador es `0` → equivale a `#DIV/0!` en Excel. La tabla termina ahí (no se hace `continue`, no se ignora la fila). En código:

```python
def _delta2(p0, p1, p2):
    denom = p2 - 2*p1 + p0
    if abs(denom) < 1e-15:
        return None   # -> break en el llamador
    return p0 - ((p1 - p0) ** 2) / denom
```

---

### 6.2 Secuencia base de Punto Fijo para Aitken y Steffensen

Ambos métodos generan primero una secuencia de Punto Fijo completa:

```
pf[0] = x0
pf[k+1] = g(pf[k])
```

Esta secuencia se genera de una vez antes de construir las filas del método, con suficientes elementos para cubrir todas las iteraciones necesarias.

---

### 6.3 Aitken (Δ²)

**Arquitectura confirmada celda a celda contra amburger.xlsx. Diferencia = 0.000e+00 en las 4 filas.**

La secuencia PF tiene `pf[0] = x0 = 1`, `pf[1] = g(x0)`, `pf[2] = g(pf[1])`, etc.

La capa Aitken **inicia en `pf[1]`, NO en `pf[0]`**. La fila k del Aitken usa el triplete:

```
ait[k] = Δ²( pf[k+1], pf[k+2], pf[k+3] )
```

Esto es lo que Excel hace: la columna B fila 2 (`B2`) usa `K2, K3, K4`, que son `pf[1], pf[2], pf[3]`.

**Arquitectura A (INCORRECTA):** `ait[k] = Δ²(pf[k], pf[k+1], pf[k+2])`
Produce diferencias de `2.381e-03`, `7.003e-05`, `2.061e-06`, `6.068e-08` contra Excel.

**Arquitectura B (CORRECTA):** `ait[k] = Δ²(pf[k+1], pf[k+2], pf[k+3])`
Produce diferencia `0.000e+00` en las cuatro filas.

Reglas adicionales de la hoja Aitken:

| Regla | Valor |
|---|---|
| Fila k=0 | sin error (columna C vacía en Excel) |
| Error inicia en | k=1: `ABS((ait[1]−ait[0])/ait[1]) × 100` |
| Detención | primer "SI" |
| `iteration_count` | índice `k` de la fila convergente (NO `len(rows) - 1`) |
| `root` | `ait[k]` de la fila convergente |

El `iteration_count` de Aitken es el índice `k` explícito de la fila donde converge, porque la arquitectura de triplete desplazado hace que `k` no coincida con `len(rows) - 1` en todos los casos.

Verificación numérica (f(x)=x²−2, g(x)=(x+2)/(x+1), x0=1):

| k | ait[k] (backend) | B_Excel | diff |
|---|---|---|---|
| 0 | 1.4142857142857144 | 1.4142857142857144 | 0.000e+00 |
| 1 | 1.4142156862745097 | 1.4142156862745097 | 0.000e+00 |
| 2 | 1.4142136248948698 | 1.4142136248948698 | 0.000e+00 |
| 3 | 1.4142135642135643 | 1.4142135642135643 | 0.000e+00 → SI |

`iteration_count = 3`, `root = 1.4142135642135643`

---

### 6.4 Steffensen

**Arquitectura de tres capas**, verificada con diff = 0.000e+00.

```
Capa 1 — Punto Fijo:
    pf[0] = x0
    pf[k+1] = g(pf[k])

Capa 2 — Aitken Δ² sobre PF  (INICIA en pf[1], no en pf[0]):
    ait[k] = Δ²( pf[k+1], pf[k+2], pf[k+3] )
    — equivalente: iterar i desde 1, ait.append(Δ²(pf[i], pf[i+1], pf[i+2]))

Capa 3 — Steffensen Δ² sobre Aitken  (INICIA en ait[0]):
    stef[k] = Δ²( ait[k], ait[k+1], ait[k+2] )
    — columna B de la hoja Excel
```

Reglas de error e `iteration_count`:
- stef[0] (k=0): sin error.
- stef[k] (k≥1): `error_pct = ABS((stef[k] − stef[k-1]) / stef[k]) × 100`.
- `iteration_count = len(rows) - 1`.
- `root = stef[k]` de la fila convergente.

La capa 2 hereda el inicio en `pf[1]` que define Aitken. Cambiar ese offset rompe Steffensen también.

---

### 6.5 Newton 2do Orden — caso especial de signo

La fórmula contiene una raíz cuadrada con dos soluciones posibles. Excel usa la rama **positiva** del discriminante con signo negativo en `f'`:

```
xₙ₊₁ = xₙ + (−f'(xₙ) + √( (f'(xₙ))² − 2·f''(xₙ)·f(xₙ) )) / f''(xₙ)
```

No usar `+f'` ni `−√`. La rama elegida produce convergencia hacia la raíz positiva de `x²−2`. Si el discriminante es negativo, el método no es aplicable para ese `x0`.

Verificación (x0=1, f(x)=x²−2):

| celda | valor backend | valor Excel | diff |
|---|---|---|---|
| F2 (x_next k=0) | 1.4142135623730951 | 1.4142135623730951 | 0.000e+00 |
| G2 (error k=0) | 29.289321881345252 | 29.289321881345252 | 0.000e+00 |
| F3 (x_next k=1) | 1.4142135623730951 | 1.4142135623730951 | 0.000e+00 |
| G3 (error k=1) | 0.0 | 0 | 0.000e+00 → SI |

`iteration_count = 1`, `root = 1.4142135623730951`

---

## 7. Tabla de `iteration_count` por método

| Método | Fórmula | Razonamiento |
|---|---|---|
| Bisección | `len(rows) - 1` | k=0 sin error; k=22 es el SI |
| Regula Falsi | `len(rows) - 1` | k=0 sin error |
| Punto Fijo | `len(rows) - 1` | k=0 sin error |
| **Aitken** | **`k` de la fila SI** | índice explícito; arquitectura de triplete desplazado |
| Steffensen | `len(rows) - 1` | k=0 sin error |
| Newton-Raphson | `len(rows) - 1` | todas las filas tienen error |
| Newton Modificado | `len(rows) - 1` | todas las filas tienen error |
| Newton 2do Orden | `len(rows) - 1` | todas las filas tienen error |
| Chebyshev | `len(rows) - 1` | todas las filas tienen error |
| Halley | `len(rows) - 1` | todas las filas tienen error |
| Super Halley | `len(rows) - 1` | todas las filas tienen error |
| Ostrowsky | `len(rows) - 1` | todas las filas tienen error |
| Secante | `len(rows) - 1` | k=0 sin error |
| Von Mises | `len(rows) - 1` | todas las filas tienen error |

---

## 8. Valores de referencia auditados (f(x)=x²−2, x0=1)

Resultados del backend en la auditoría final, diferencia 0.000e+00 contra amburger.xlsx en los tres campos:

| # | Método | root | final_error_pct | iteration_count |
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

---

## 9. Reglas de cambio futuro

Cualquier modificación al backend debe respetar estas restricciones. Si se rompe alguna, la auditoría automatizada fallará.

**NUNCA cambiar sin re-auditar:**

1. `_TOLERANCE = 0.00001` — no usar `1e-5` como variable configurable sin mantener este valor como default.
2. `_MAX_ITER = 25` — el mismo.
3. La fórmula de error: el denominador es siempre `x_nuevo`, no `x_anterior`.
4. La condición de convergencia: `error_pct < tol` (estrictamente menor, como `IF(C < 0.00001, "SI",...)`).
5. El método para en el **primer SI** — no acumula filas adicionales después.
6. `iteration_count = len(rows) - 1` en todos los métodos excepto Aitken.
7. Aitken: la capa base inicia en `pf[1]` — cambiar a `pf[0]` introduce diferencias de `~2.4e-3`.
8. Steffensen: hereda el inicio en `pf[1]` de la capa Aitken — si se cambia Aitken, Steffensen se rompe también.
9. Newton 2do Orden: la rama de la raíz es `−f' + √discriminante`, no `+f'`.
10. Von Mises: `f'(x₀)` se calcula **una sola vez** al inicio — no recalcular en cada iteración.
11. Secante: las filas k=0 y k=1 usan evaluación directa de `f` (sin IFERROR); las filas k≥2 usan fallback `IFERROR(..., 0)` para `f` y `IFERROR(..., xk)` para `x_next`.

**Para agregar un método nuevo:**
- Reproducir primero la hoja Excel completa con `data_only=True`.
- Verificar diff = 0.000e+00 celda a celda antes de declararlo validado.
- Agregar su fila a la tabla §8.
- La auditoría de regresión corre los 14 métodos existentes — debe seguir siendo 14/14 después del cambio.
