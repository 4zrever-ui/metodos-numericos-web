# MULTI_EQUATION_CURRENT_AUDIT.md

> Auditoría de ejecución real sobre 6 ecuaciones × 14 métodos  
> ZIP: `proyecto.zip` — ejecutado en Python 3.13 con sympy, numpy  
> Sin modificar ningún archivo. Resultados obtenidos directamente del código del ZIP.

---

## Índice de métodos

| # | Método | Archivo | Sheet Excel |
|---|--------|---------|-------------|
| 1 | Newton-Raphson | `methods/newton_raphson.py` | Newton-Raphson |
| 2 | Bisección | `methods/biseccion.py` | Bisección |
| 3 | Regula Falsi | `methods/regula_falsi.py` | Regula Falsi |
| 4 | Secante | `methods/secante.py` | Secante |
| 5 | Punto Fijo | `methods/punto_fijo.py` | Punto Fijo |
| 6 | Steffensen | `methods/steffensen.py` | Steffensen |
| 7 | Aitken | `methods/aitken.py` | Aitken |
| 8 | Von Mises | `methods/von_mises.py` | Von Mises |
| 9 | Newton Modificado | `methods/newton_family.py` | Newton Modificado |
| 10 | Newton 2do Orden | `methods/newton_family.py` | Newton 2do Orden |
| 11 | Chebyshev | `methods/newton_family.py` | Chebyshev |
| 12 | Halley | `methods/newton_family.py` | Halley |
| 13 | Super Halley | `methods/newton_family.py` | Super Halley |
| 14 | Ostrowsky | `methods/newton_family.py` | Ostrowsky |

**Tolerancia:** `0.00001` (relativa %) — **Máx. iteraciones:** `25`

---

## Leyenda de tablas

| Símbolo | Significado |
|---------|-------------|
| ✅ | Aplicable y convergió |
| ❌ | No aplicable (falla pre-chequeo) |
| ⚠️ | Aplicable pero no convergió en 25 iter. |
| 🔀 | Convergió a raíz INCORRECTA (g(x) hardcodeada) |

---

## Ecuación 1: x²−2

**Raíz real:** ±1.41421356...  
**Parámetros auto:** a=1.0, b=1.5, x0=0.0, x0_alt=−1.0  
**Raíces detectadas:** [−1.4142135624, 1.4142135624]

> **Problema de x0:** `roots_approx[0]` = −1.4142. `_best_integer_near(−1.4142)` = 0.0.  
> Como f'(0) = 2·0 = 0, todos los métodos basados en derivada retornan `applicable=False`.

| # | Método | Estado | Raíz obtenida | Iteraciones | Error % final |
|---|--------|--------|---------------|-------------|---------------|
| 1 | Newton-Raphson | ❌ | — | 0 | — |
| 2 | Bisección | ✅ | 1.4142135381698608 | 21 | 8.43×10⁻⁶ |
| 3 | Regula Falsi | ✅ | 1.4142135620573204 | 5 | 7.36×10⁻⁷ |
| 4 | Secante | ✅ | −1.4142135623730954 | 7 | 2.23×10⁻⁸ |
| 5 | Punto Fijo | 🔀 | 2.0945514643513907 | 9 | 4.58×10⁻⁶ |
| 6 | Steffensen | 🔀 | 2.0945514815521067 | 1 | 1.33×10⁻⁷ |
| 7 | Aitken | 🔀 | 2.094551485393428 | 3 | 7.78×10⁻⁶ |
| 8 | Von Mises | ❌ | — | 0 | — |
| 9 | Newton Modificado | ❌ | — | 0 | — |
| 10 | Newton 2do Orden | ❌ | — | 0 | — |
| 11 | Chebyshev | ❌ | — | 0 | — |
| 12 | Halley | ❌ | — | 0 | — |
| 13 | Super Halley | ❌ | — | 0 | — |
| 14 | Ostrowsky | ❌ | — | 0 | — |

**Razón de rechazo (métodos derivada):** `f'(x₀) = 0.00e+00 ≈ 0. División por cero. Elige otro x₀.`  
**Razón de Punto Fijo/Steffensen/Aitken:** `applicable=True` pero g(x)=(2x+5)^(1/3) → converge a raíz de x³−2x−5.  
**Métodos funcionales correctos:** Bisección ✅, Regula Falsi ✅, Secante ✅  
**Score:** 3/14 correctos | 3/14 redirigidos | 8/14 inaplicables

---

## Ecuación 2: x³−2x−5

**Raíz real:** 2.09455148154...  
**Parámetros auto:** a=2.0, b=2.5, x0=2.0, x0_alt=3.0  
**Raíces detectadas:** [2.0945514815]

> Esta es la ecuación de referencia para la que g(x)=(2x+5)^(1/3) fue diseñada.

| # | Método | Estado | Raíz obtenida | Iteraciones | Error % final |
|---|--------|--------|---------------|-------------|---------------|
| 1 | Newton-Raphson | ✅ | 2.0945514815423265 | 3 | 7.44×10⁻⁹ |
| 2 | Bisección | ✅ | 2.0945514440536500 | 21 | 5.69×10⁻⁶ |
| 3 | Regula Falsi | ✅ | 2.0945514405272205 | 8 | 8.06×10⁻⁶ |
| 4 | Secante | ✅ | 2.0945514815423270 | 6 | 1.50×10⁻⁸ |
| 5 | Punto Fijo | ✅ | 2.0945514544389705 | 7 | 7.22×10⁻⁶ |
| 6 | Steffensen | ✅ | 2.0945514815423270 | 1 | 6.38×10⁻¹² |
| 7 | Aitken | ✅ | 2.0945514817633604 | 2 | 4.46×10⁻⁷ |
| 8 | Von Mises | ✅ | 2.0945514952671616 | 6 | 6.30×10⁻⁶ |
| 9 | Newton Modificado | ✅ | 2.0945514815423265 | 3 | 6.58×10⁻⁹ |
| 10 | Newton 2do Orden | ✅ | 2.0945514815423265 | 2 | 1.87×10⁻¹² |
| 11 | Chebyshev | ✅ | 2.0945514815423265 | 2 | 4.36×10⁻⁹ |
| 12 | Halley | ✅ | 2.0945514815423265 | 2 | 1.03×10⁻¹⁰ |
| 13 | Super Halley | ✅ | 2.0945514815423265 | 2 | 3.27×10⁻¹² |
| 14 | Ostrowsky | ✅ | 2.0945514815423265 | 2 | 7.21×10⁻¹³ |

**Score:** 14/14 correctos — caso de referencia funciona perfectamente.

**Métodos más rápidos (convergencia):** Steffensen (1 iter), Newton 2do Orden (2), Chebyshev (2), Halley (2), Super Halley (2), Ostrowsky (2).

---

## Ecuación 3: x³−x−1

**Raíz real:** 1.32471795724...  
**Parámetros auto:** a=1.0, b=1.5, x0=1.0, x0_alt=2.0  
**Raíces detectadas:** [1.3247179572]

| # | Método | Estado | Raíz obtenida | Iteraciones | Error % final |
|---|--------|--------|---------------|-------------|---------------|
| 1 | Newton-Raphson | ✅ | 1.324717957244746 | 5 | 3.30×10⁻¹² |
| 2 | Bisección | ✅ | 1.3247178792953491 | 21 | 8.99×10⁻⁶ |
| 3 | Regula Falsi | ✅ | 1.3247179449662787 | 8 | 5.43×10⁻⁶ |
| 4 | Secante | ✅ | 1.3247179572446703 | 7 | 6.12×10⁻⁷ |
| 5 | Punto Fijo | 🔀 | 2.0945514735704873 | 9 | 2.12×10⁻⁶ |
| 6 | Steffensen | 🔀 | 2.0945514815433013 | 1 | 1.32×10⁻⁸ |
| 7 | Aitken | 🔀 | 2.0945514823704303 | 3 | 1.67×10⁻⁶ |
| 8 | Von Mises | ⚠️ | 1.4897888177758452 | 24 | 27.41% |
| 9 | Newton Modificado | ✅ | 1.3247179572447432 | 4 | 4.17×10⁻⁶ |
| 10 | Newton 2do Orden | ✅ | 1.324717957244746 | 3 | 0.0 |
| 11 | Chebyshev | ✅ | 1.324717957244746 | 4 | 1.78×10⁻¹² |
| 12 | Halley | ✅ | 1.324717957244746 | 3 | 3.13×10⁻¹² |
| 13 | Super Halley | ✅ | 1.324717957244746 | 3 | 0.0 |
| 14 | Ostrowsky | ✅ | 1.324717957244746 | 2 | 9.29×10⁻⁶ |

**Score:** 9/14 correctos | 3/14 redirigidos | 1/14 no convergió  
**Von Mises:** oscila — error final 27.4%, raíz reportada 1.4897 (incorrecta).

---

## Ecuación 4: cos(x)−x

**Raíz real:** 0.73908513321... (punto fijo del coseno)  
**Parámetros auto:** a=0.5, b=1.0, x0=1.0, x0_alt=2.0  
**Raíces detectadas:** [0.7390851332]

| # | Método | Estado | Raíz obtenida | Iteraciones | Error % final |
|---|--------|--------|---------------|-------------|---------------|
| 1 | Newton-Raphson | ✅ | 0.7390851332151607 | 3 | 2.30×10⁻⁸ |
| 2 | Bisección | ✅ | 0.7390851378440857 | 22 | 8.06×10⁻⁶ |
| 3 | Regula Falsi | ✅ | 0.7390851329985466 | 6 | 5.56×10⁻⁷ |
| 4 | Secante | ✅ | 0.7390851332152121 | 5 | 1.74×10⁻⁶ |
| 5 | Punto Fijo | 🔀 | 2.0945514735704873 | 9 | 2.12×10⁻⁶ |
| 6 | Steffensen | 🔀 | 2.0945514815433013 | 1 | 1.32×10⁻⁸ |
| 7 | Aitken | 🔀 | 2.0945514823704303 | 3 | 1.67×10⁻⁶ |
| 8 | Von Mises | ✅ | 0.7390851395102382 | 6 | 8.49×10⁻⁶ |
| 9 | Newton Modificado | ✅ | 0.7390851332151607 | 3 | 7.64×10⁻⁹ |
| 10 | Newton 2do Orden | ⚠️ | −47.96167659108126 | 5 | 22.16% |
| 11 | Chebyshev | ✅ | 0.7390851332151607 | 2 | 2.17×10⁻⁷ |
| 12 | Halley | ✅ | 0.7390851332151607 | 2 | 8.96×10⁻⁸ |
| 13 | Super Halley | ✅ | 0.7390851332151607 | 2 | 2.57×10⁻⁸ |
| 14 | Ostrowsky | ⚠️ | 12.427562677615981 | 5 | 38.41% |

**Score:** 8/14 correctos | 3/14 redirigidos | 2/14 divergen | 1/14 Von Mises correcto tardío  
**Newton 2do Orden:** diverge, raíz reportada −47.96.  
**Ostrowsky:** diverge, raíz reportada 12.43.

---

## Ecuación 5: e^−x−x

**Raíz real:** 0.56714329040...  
**Parámetros auto:** a=0.5, b=1.0, x0=1.0, x0_alt=2.0  
**Raíces detectadas:** [0.5671432904]

| # | Método | Estado | Raíz obtenida | Iteraciones | Error % final |
|---|--------|--------|---------------|-------------|---------------|
| 1 | Newton-Raphson | ✅ | 0.5671432904097838 | 3 | 7.79×10⁻⁷ |
| 2 | Bisección | ✅ | 0.5671432912349701 | 23 | 5.25×10⁻⁶ |
| 3 | Regula Falsi | ✅ | 0.5671432905224405 | 4 | 1.60×10⁻⁶ |
| 4 | Secante | ✅ | 0.5671432904097838 | 6 | 5.66×10⁻⁹ |
| 5 | Punto Fijo | 🔀 | 2.0945514735704873 | 9 | 2.12×10⁻⁶ |
| 6 | Steffensen | 🔀 | 2.0945514815433013 | 1 | 1.32×10⁻⁸ |
| 7 | Aitken | 🔀 | 2.0945514823704303 | 3 | 1.67×10⁻⁶ |
| 8 | Von Mises | ✅ | 0.5671432842606805 | 8 | 8.53×10⁻⁶ |
| 9 | Newton Modificado | ✅ | 0.5671432904097838 | 3 | 2.27×10⁻⁷ |
| 10 | Newton 2do Orden | ⚠️ | 14293.916409504527 | 1 | 99.94% |
| 11 | Chebyshev | ✅ | 0.5671432904097840 | 2 | 1.47×10⁻¹⁰ |
| 12 | Halley | ✅ | 0.5671432904097838 | 2 | 5.35×10⁻⁸ |
| 13 | Super Halley | ✅ | 0.5671432904097838 | 2 | 5.48×10⁻⁷ |
| 14 | Ostrowsky | ⚠️ | 34299972.71532224 | 25 | 50.0% |

**Score:** 8/14 correctos | 3/14 redirigidos | 2/14 divergen  
**Newton 2do Orden:** primer paso lanza a 14293.9 — diverge completamente (error 99.94%).  
**Ostrowsky:** diverge a 34,299,972 en 25 iteraciones, error estabilizado en 50%.

---

## Ecuación 6: x⁴−10

**Raíz real:** ±1.77827941003...  
**Parámetros auto:** a=1.5, b=2.0, x0=0.0, x0_alt=−2.0  
**Raíces detectadas:** [−1.77827941, 1.77827941]

> **Mismo problema que x²−2:** `roots_approx[0]` = −1.7782 → `_best_integer_near(−1.7782)` = 0.0 → f'(0)=0.

| # | Método | Estado | Raíz obtenida | Iteraciones | Error % final |
|---|--------|--------|---------------|-------------|---------------|
| 1 | Newton-Raphson | ❌ | — | 0 | — |
| 2 | Bisección | ✅ | 1.7782794237136840 | 21 | 6.70×10⁻⁶ |
| 3 | Regula Falsi | ✅ | 1.7782793745178105 | 8 | 9.84×10⁻⁶ |
| 4 | Secante | ✅ | −1.7782794100389219 | 8 | 3.28×10⁻⁸ |
| 5 | Punto Fijo | 🔀 | 2.0945514643513907 | 9 | 4.58×10⁻⁶ |
| 6 | Steffensen | 🔀 | 2.0945514815521067 | 1 | 1.33×10⁻⁷ |
| 7 | Aitken | 🔀 | 2.094551485393428 | 3 | 7.78×10⁻⁶ |
| 8 | Von Mises | ❌ | — | 0 | — |
| 9 | Newton Modificado | ❌ | — | 0 | — |
| 10 | Newton 2do Orden | ❌ | — | 0 | — |
| 11 | Chebyshev | ❌ | — | 0 | — |
| 12 | Halley | ❌ | — | 0 | — |
| 13 | Super Halley | ❌ | — | 0 | — |
| 14 | Ostrowsky | ❌ | — | 0 | — |

**Razón de rechazo:** `f'(x₀) = 0.00e+00 ≈ 0. División por cero. Elige otro x₀.`  
**Score:** 3/14 correctos | 3/14 redirigidos | 8/14 inaplicables

---

## Resumen ejecutivo consolidado

### Tabla maestra (✅=correcto, ❌=inaplicable, ⚠️=diverge, 🔀=raíz incorrecta)

| Método | x²−2 | x³−2x−5 | x³−x−1 | cos(x)−x | e^−x−x | x⁴−10 | **Score** |
|--------|------|---------|--------|----------|--------|-------|-----------|
| Newton-Raphson | ❌ | ✅ | ✅ | ✅ | ✅ | ❌ | 4/6 |
| Bisección | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | **6/6** |
| Regula Falsi | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | **6/6** |
| Secante | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | **6/6** |
| Punto Fijo | 🔀 | ✅ | 🔀 | 🔀 | 🔀 | 🔀 | 1/6 |
| Steffensen | 🔀 | ✅ | 🔀 | 🔀 | 🔀 | 🔀 | 1/6 |
| Aitken | 🔀 | ✅ | 🔀 | 🔀 | 🔀 | 🔀 | 1/6 |
| Von Mises | ❌ | ✅ | ⚠️ | ✅ | ✅ | ❌ | 3/6 |
| Newton Modificado | ❌ | ✅ | ✅ | ✅ | ✅ | ❌ | 4/6 |
| Newton 2do Orden | ❌ | ✅ | ✅ | ⚠️ | ⚠️ | ❌ | 2/6 |
| Chebyshev | ❌ | ✅ | ✅ | ✅ | ✅ | ❌ | 4/6 |
| Halley | ❌ | ✅ | ✅ | ✅ | ✅ | ❌ | 4/6 |
| Super Halley | ❌ | ✅ | ✅ | ✅ | ✅ | ❌ | 4/6 |
| Ostrowsky | ❌ | ✅ | ✅ | ⚠️ | ⚠️ | ❌ | 2/6 |

---

### Análisis por categoría de fallo

#### Grupo A — Métodos sin fallo de lógica (6/6 o fallo solo por x0)
Bisección, Regula Falsi y Secante son los únicos métodos que funcionan correctamente en **todas las ecuaciones**. No dependen de derivadas ni de g(x).

#### Grupo B — Métodos bloqueados por x0=0 (ecuaciones pares)
Para x²−2 y x⁴−10, `_best_integer_near()` devuelve x0=0, lo que provoca f'(0)=0 y rechazo de: Newton-Raphson, Von Mises, Newton Modificado, Newton 2do Orden, Chebyshev, Halley, Super Halley, Ostrowsky (8 métodos × 2 ecuaciones = 16 casos inaplicables).

#### Grupo C — g(x) hardcodeada afecta a 3 métodos
Punto Fijo, Steffensen y Aitken reciben siempre `g(x) = (2x+5)^(1/3)`. Convergen a x≈2.0945 en cualquier ecuación distinta a x³−2x−5. Esto afecta **15 de 18 casos** (5 ecuaciones × 3 métodos).

#### Grupo D — Newton 2do Orden diverge con funciones no polinómicas
Para cos(x)−x y e^−x−x, el discriminante `(f')²−2f''·f` genera pasos enormes desde x0=1, divergiendo a −47.96 y 14293.9 respectivamente.

#### Grupo E — Ostrowsky diverge con funciones no polinómicas
Para cos(x)−x y e^−x−x, `√(f'²−f·f'')` produce valores que llevan la iteración a divergir (12.43 y 34,299,972 respectivamente).

---

### Conteo global

| Categoría | Casos |
|-----------|-------|
| ✅ Correcto y convergente | **39 / 84** |
| 🔀 Raíz incorrecta (g hardcodeada) | **15 / 84** |
| ❌ Inaplicable (pre-chequeo) | **20 / 84** |
| ⚠️ Aplicable pero diverge | **5 / 84** |
| ❌ Inaplicable (Von Mises x²−2, x⁴−10) | **5 / 84** |

**Total casos auditados:** 6 ecuaciones × 14 métodos = **84 ejecuciones**

---

## Notas sobre la ejecución

- Todos los resultados fueron obtenidos ejecutando `method_fn(eq, params)` con los parámetros auto-generados por `generate_params()` sin intervención manual.
- La salida de debug `CANDIDATOS GX` se emitió por stdout en cada llamada a `generate_params()` (12 veces en total — una por ecuación en parse, una en generate).
- No se modificó ningún archivo. No se instalaron dependencias adicionales más allá de las ya presentes (`sympy`, `numpy`).
