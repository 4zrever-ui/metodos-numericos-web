# AUTO_PARAMS_CURRENT_STATE.md

> Auditoría del estado real de `backend/core/auto_params.py`  
> ZIP: `proyecto.zip` — fecha archivo: 2026-06-06 05:45  
> Evidencia obtenida leyendo el código fuente y ejecutando el módulo.

---

## 1. Encabezado y constantes del módulo

```python
"""
Auto-parameter generator.
Finds roots, valid intervals [a,b], initial approximations, and g(x) candidates.
Priority: positive integers → non-negative integers → negative integers → decimals.
"""
```

**Imports activos:** `math`, `dataclasses`, `typing`, `numpy`, `sympy`, `equation_parser`.

**`_SEARCH_RANGE`** (definida pero **no usada** en ninguna función del módulo):
```python
_SEARCH_RANGE = [
    *range(1, 11),          # 1..10
    *range(0, -11, -1),     # 0..-10
    *[i / 2 for i in range(-21, 22)],  # -10.5..10.5 step 0.5
]
```

---

## 2. Estado real de `_generate_gx_candidates()`

### 2.1 Código activo

```python
def _generate_gx_candidates(eq: ParsedEquation, root: float) -> list[dict]:
    candidates = []
    f = eq.f_sympy
    x = _x

    # Estrategia activa — hardcodeada para x³−2x−5
    try:
        g = (2*x + 5)**(sp.Rational(1, 3))
        gp = sp.diff(g, x)
        gp_val = abs(float(gp.subs(x, root).evalf()))
        candidates.append({
            "expr": g,
            "label": "(2x+5)^(1/3)",
            "gp_abs": gp_val,
            "converges": gp_val < 1,
        })
    except Exception:
        pass

    candidates.sort(key=lambda c: (0 if c["converges"] else 1, c["gp_abs"]))
    print("\nCANDIDATOS GX")
    for c in candidates:
        print(c["label"], c["gp_abs"])

    return candidates
```

### 2.2 Estrategias DESACTIVADAS (comentadas)

Las siguientes tres estrategias están completamente comentadas con la etiqueta `# DESACTIVADO TEMPORALMENTE`:

| # | Estrategia | Descripción |
|---|-----------|-------------|
| 1 | `x - f(x)/f'(x)` | Corrección Newton — siempre converge si f'≠0 |
| 2 | `sp.solve(f, x)` | Despejar x algebraicamente de cada término |
| 3 | `x - c·f(x)` donde c = 1/f'(root) | Contracción lineal calibrada en la raíz |

### 2.3 Comportamiento observado en ejecución real

La función siempre retorna **exactamente un candidato**: `(2x+5)^(1/3)`, independientemente de la ecuación de entrada.

| Ecuación | g(x) retornada | \|g'(root)\| | ¿Converge? |
|----------|---------------|-------------|-----------|
| x²−2 | (2x+5)^(1/3) | ~0.152 | ✅ Sí |
| x³−2x−5 | (2x+5)^(1/3) | ~0.152 | ✅ Sí |
| x³−x−1 | (2x+5)^(1/3) | ~0.152 | ✅ Sí |
| cos(x)−x | (2x+5)^(1/3) | ~0.152 | ✅ Sí |
| e^−x−x | (2x+5)^(1/3) | ~0.152 | ✅ Sí |
| x⁴−10 | (2x+5)^(1/3) | ~0.152 | ✅ Sí |

**Consecuencia crítica:** Para Punto Fijo, Steffensen y Aitken, `g(x) = (2x+5)^(1/3)` es aplicada a **cualquier ecuación**. Esto produce raíces correctas solo para x³−2x−5 (la ecuación para la que fue diseñada). Para las demás ecuaciones, los tres métodos convergen a `x ≈ 2.0945` (raíz de x³−2x−5), no a la raíz de la ecuación solicitada.

**Print de debug activo:** La función emite por stdout `\nCANDIDATOS GX` seguido del label y valor de |g'|. Este print no está guardado en silencio; sale directo a la consola del servidor en producción.

---

## 3. Estado real de `_best_integer_near()`

### 3.1 Ubicación en el archivo

La función está **definida al final del archivo**, después de `generate_params()`. Es llamada dentro de `generate_params()` antes de estar definida textualmente — esto funciona en Python porque `generate_params` es una función (no código de módulo top-level), pero es una estructura atípica.

### 3.2 Código completo

```python
def _best_integer_near(val: float, exclude: Optional[float] = None) -> float:
    """Return the best integer near val, preferring positive, excluding one value."""
    candidates = [
        math.floor(val),
        math.ceil(val),
        round(val),
        math.floor(val) - 1,
        math.ceil(val) + 1,
    ]
    candidates = [c for c in candidates if exclude is None or c != exclude]
    candidates.sort(key=lambda c: (0 if c > 0 else (1 if c == 0 else 2), abs(c - val)))
    return float(candidates[0]) if candidates else val
```

### 3.3 Lógica de ordenamiento

Ordena por tupla `(prioridad_signo, distancia)`:
- `0` → entero positivo (prioridad máxima)
- `1` → cero
- `2` → entero negativo
- Desempate: menor `|c - val|`

### 3.4 Comportamiento observado

| Ecuación | root_ref | x0 calculado | x0_alt calculado |
|----------|----------|-------------|----------------|
| x²−2 | ±1.4142 | 0.0 | −1.0 |
| x³−2x−5 | 2.0945 | 2.0 | 3.0 |
| x³−x−1 | 1.3247 | 1.0 | 2.0 |
| cos(x)−x | 0.7390 | 1.0 | 2.0 |
| e^−x−x | 0.5671 | 1.0 | 2.0 |
| x⁴−10 | ±1.7782 | 0.0 | −2.0 |

**Anomalía en x²−2 y x⁴−10:** `roots_approx` contiene dos raíces (±). La primera raíz tomada es la negativa (−1.4142 para x²−2, −1.7782 para x⁴−10). `_best_integer_near(−1.4142)` retorna `0.0` (cero tiene prioridad sobre enteros negativos), lo cual hace que `f'(0)=0` para ambas ecuaciones, dejando inaplicables todos los métodos basados en derivada.

---

## 4. Estado real de `generate_params()`

### 4.1 Grid de búsqueda

```python
grid_ints = list(range(-15, 16))          # −15 a 15, enteros
grid_fine = [i * 0.5 for i in range(-30, 31)]  # −15.0 a 15.0, paso 0.5
grid = sorted(set(grid_ints + grid_fine))  # unión, ordenada
```
Total: 61 puntos (−15.0 a 15.0, paso 0.5).

### 4.2 Flujo de ejecución

```
1. _find_sign_changes(eq, grid)
2. Si hay cambios de signo → _bisect_approx() por cada par (máx 4)
3. sp.solve(eq.f_sympy, x) → raíces exactas adicionales
4. Si sin raíces → fallback: mínimo |f(x)| en grid
5. Selección de [a,b] → par con mejor score (enteros positivos primero)
6. x0 = _best_integer_near(roots_approx[0])
7. x0_alt = _best_integer_near(roots_approx[0], exclude=x0)
8. gx_candidates = _generate_gx_candidates(eq, root_ref)
```

### 4.3 Parámetros fijos

| Parámetro | Valor |
|-----------|-------|
| `tol` | `0.00001` |
| `max_iter` | `25` |
| `x0_von_mises` | igual a `x0` |

### 4.4 Parámetros auto-generados por ecuación

| Ecuación | a | b | x0 | x0_alt | roots_approx |
|----------|---|---|----|--------|--------------|
| x²−2 | 1.0 | 1.5 | 0.0 | −1.0 | [−1.4142, 1.4142] |
| x³−2x−5 | 2.0 | 2.5 | 2.0 | 3.0 | [2.0945] |
| x³−x−1 | 1.0 | 1.5 | 1.0 | 2.0 | [1.3247] |
| cos(x)−x | 0.5 | 1.0 | 1.0 | 2.0 | [0.7390] |
| e^−x−x | 0.5 | 1.0 | 1.0 | 2.0 | [0.5671] |
| x⁴−10 | 1.5 | 2.0 | 0.0 | −2.0 | [−1.7782, 1.7782] |

---

## 5. Hallazgos críticos (sin propuestas de cambio)

### H-1: g(x) hardcodeada para una sola ecuación
`_generate_gx_candidates()` solo genera `(2x+5)^(1/3)`. Las tres estrategias genéricas están desactivadas. Resultado: Punto Fijo, Steffensen y Aitken convergen siempre a la raíz de x³−2x−5, no a la raíz de la ecuación solicitada (excepto cuando la ecuación es x³−2x−5).

### H-2: x0=0 para ecuaciones pares simétricas
Para x²−2 y x⁴−10, `roots_approx[0]` es el valor negativo (el primero en la lista retornada por `sp.solve`). `_best_integer_near()` prioriza cero sobre enteros negativos, resultando en x0=0. Como f'(0)=0 para ambas ecuaciones, todos los métodos basados en derivada retornan `applicable=False`.

### H-3: Print de debug en producción
`_generate_gx_candidates()` contiene `print("\nCANDIDATOS GX")` y `print(c["label"], c["gp_abs"])` activos. Este output aparece en stdout del servidor FastAPI en cada llamada a cualquier endpoint de método.

### H-4: `_SEARCH_RANGE` definida pero no usada
La constante `_SEARCH_RANGE` al inicio del módulo no es referenciada en ninguna función. El grid efectivo se construye localmente en `generate_params()`.

### H-5: Orden de definición atípico
`_best_integer_near()` se define **después** de `generate_params()` en el archivo, aunque es llamada por ella. Funciona en Python por el mecanismo de closures de funciones, pero es inusual.
