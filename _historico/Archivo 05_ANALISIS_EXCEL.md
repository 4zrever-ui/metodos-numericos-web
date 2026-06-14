El archivo contiene **14 hojas** en el siguiente orden:

| # | Nombre de hoja | Tipo | Columnas usadas | Filas de datos |

|---|---------------|------|-----------------|----------------|

| 1 | Bisección | Intervalo | A–J | 2–24 (23 iter.) |

| 2 | Regula Falsi | Intervalo | A–J | 2–11 (10 iter.) |

| 3 | Punto Fijo | Iterativo | A–E | 2–11 (10 iter.) |

| 4 | Aitken | Aceleración (Δ²) | A–D + I–M | 2–5 |

| 5 | Steffensen | Aceleración (Δ²) | A–D + I–L | 2–3 |

| 6 | Newton-Raphson | Derivada 1ª | A–G | 2–6 (5 iter.) |

| 7 | Newton Modificado | Derivada 1ª y 2ª | A–H | 2–6 (5 iter.) |

| 8 | Newton 2do Orden | Derivada cuadrática | A–H | 2–3 (2 iter.) |

| 9 | Chebyshev | Derivada 1ª y 2ª | A–H | 2–5 (4 iter.) |

| 10 | Halley | Derivada 1ª y 2ª | A–H | 2–5 (4 iter.) |

| 11 | Super Halley | Derivada 1ª y 2ª | A–H | 2–4 (3 iter.) |

| 12 | Ostrowsky | Derivada 1ª y 2ª | A–H | 3–5 (3 iter.) |

| 13 | Secante | Dos puntos iniciales | A–H | 2–8 (7 iter.) |

| 14 | Von Mises | Derivada fija en x₀ | A–G | 2–19 (18 iter.) |

**Ecuación de prueba usada en TODO el archivo:** `f(x) = x² − 2 = 0` → raíz: √2 ≈ 1.41421356...

---

## 2. PALETA DE COLORES EXACTA POR HOJA

### Sistema de colores del archivo

Cada hoja tiene su propio **color temático único**. El esquema usa dos tonos: encabezado oscuro (header), celda data alternada (light1 / light2), y una franja inferior de título/info en color sólido.

| Hoja | Color Header (fila 1) | Color Filas Par | Color Filas Impar | Color Título/Footer |

|------|-----------------------|-----------------|-------------------|---------------------|

| Bisección | `#D6EAF8` (azul pálido) | `#EBF5FB` | `#D6EAF8` | `#1A5276` (azul oscuro) |

| Regula Falsi | `#D5F5E3` (verde pálido) | `#EAFAF1` | `#D5F5E3` | `#147F57` (verde oscuro) |

| Punto Fijo | `#E8DAEF` (púrpura pálido) | `#F4EBFD` | `#E8DAEF` | `#6C3483` (púrpura oscuro) |

| Aitken | `#D1F2EB` (turquesa pálido) | `#E8F8F5` | `#D1F2EB` | `#147F57` (verde oscuro) |

| Steffensen | `#D1F2EB` (turquesa pálido) | `#D3EAFD` | `#D1F2EB` | `#147F57` (verde oscuro) |

| Newton-Raphson | `#D6DBFF` (azul lila pálido) | `#EEF0FF` | `#D6DBFF` | `#1F3A93` (azul índigo) |

| Newton Modificado | `#E74C3C` (rojo claro) | `#FADBD8` | `#FDEDEC` | `#922B21` (rojo oscuro) |

| Newton 2do Orden | `#D5F5E3` (verde pálido) | `#EAFAF1` | `#D5F5E3` | `#0D553B` (verde muy oscuro) |

| Chebyshev | `#D2E4F8` (azul pálido) | sin fill | sin fill | `#174969` (azul acero) |

| Halley | `#E8F5D6` (verde lima pálido) | `#F0FAE8` | `#E8F5D6` | `#4D6A1F` (verde oliva) |

| Super Halley | `#FADBD8` (rosa pálido) | `#FEF5F5` | `#FADBD8` | `#7B241C` (rojo vino) |

| Ostrowsky | `#E8DAEF` (lila pálido) | `#F5EEF8` | `#E8DAEF` | `#4A235A` (violeta oscuro) |

| Secante | `#D1F2EB` (turquesa pálido) | `#E8F8F5` | `#D1F2EB` | `#0D553B` (verde muy oscuro) |

| Von Mises | `#D6EAF8` (azul pálido) | `#EBF5FB` | `#D6EAF8` | `#1A5276` (azul oscuro) |

### Colores texto y labels de info

- **Texto de datos:** `#1A1A2E` (azul marino casi negro) — en todas las hojas

- **Texto de título/footer (header row mergeada):** `#FFFFFF` (blanco) sobre fondo sólido oscuro

- **Labels de parámetros (Ecuación:, Intervalo:, etc.):** color secundario de cada hoja

- **Texto en etiquetas de parámetros (Bisección):** `#2E86C1` | (Newton-Raphson): `#3455DB`

---

## 3. ESTRUCTURA VISUAL POR TIPO DE HOJA

### Patrón A: Métodos de Intervalo (Bisección, Regula Falsi)

```

Fila 1:    [ENCABEZADOS — color header sólido]

Fila 2:    k=0  a₀  c₀  b₀  f(a₀)  f(c₀)  f(b₀)  f(a)·f(c)  [sin error, sin conv]

Fila 3:    k=1  ...  ...  (con Error% y Convergencia)

...

Fila n:    k=n-2

Fila n+1:  [TÍTULO MÉTODO — celda mergeada A:J, blanco sobre color sólido oscuro]

Fila n+2:  Ecuación: | valor | Intervalo inicial: | valor | Tolerancia/Fórmula: | valor

```

### Patrón B: Métodos Iterativos simples (Punto Fijo)

```

Fila 1:    [ENCABEZADOS] k | xₖ | g(xₖ) | Error % | Convergencia

Fila 2:    k=0  x₀  g(x₀)  [sin error]

Fila 3:    k=1  x₁=g(x₀)  g(x₁)  Error%  Conv

...

Fila n+1:  [TÍTULO MÉTODO — mergeada A:F]

Fila n+2:  Ecuación: | f(x) | g(x): | g(x)=...

```

### Patrón C: Métodos con Derivadas (Newton-Raphson, Newton Mod., Chebyshev, Halley, etc.)

```

Fila 1:    [ENCABEZADOS] k | xₖ | f(xₖ) | f'(xₖ) | [f''(xₖ)] | xₖ₊₁ | Error % | Conv

Fila 2:    k=0  x₀  f(x₀)  f'(x₀)  [f''(x₀)]  x₁  Error%  Conv

...

Fila n+1:  [TÍTULO MÉTODO — mergeada A:G o A:H]

Fila n+2:  Ecuación: | valor | Fórmula: | valor

Fila n+3:  [info adicional o f''(x) hardcoded]

```

### Patrón D: Método de la Secante

```

Fila 1:    k | xₖ | f(xₖ) | xₖ₋₁ (prev) | f(xₖ₋₁) | xₖ₊₁ | Error % | Conv

Fila 2:    k=0  x₀  f(x₀)  [sin prev, sin xₖ₊₁ en k=0]

Fila 3:    k=1  x₁  f(x₁)  x₀  f(x₀)  x₂  Error%  Conv

...

```

---

## 4. FÓRMULAS EXACTAS CELDA POR CELDA

### 4.1 BISECCIÓN (Hoja 1)

**Fila de inicio de iteración k=0: fila 2**

| Celda | Fórmula / Valor |

|-------|----------------|

| A2 | `0` (hardcoded) |

| B2 | `1` (hardcoded — a₀) |

| C2 | `=(B2+D2)/2` |

| D2 | `2` (hardcoded — b₀) |

| E2 | `=B2^2-2` |

| F2 | `=C2^2-2` |

| G2 | `=D2^2-2` |

| H2 | `=E2*F2` |

| I2 | *(vacío — sin error en k=0)* |

| J2 | *(vacío — sin convergencia en k=0)* |

**Fila k=1 (fila 3) en adelante — patrón repetible:**

| Celda | Fórmula |

|-------|---------|

| A(i) | `i-2` (secuencia: 0,1,2,...) |

| B(i) | `=IF(E(i-1)*F(i-1)<0, B(i-1), C(i-1))` |

| C(i) | `=(B(i)+D(i))/2` |

| D(i) | `=IF(E(i-1)*F(i-1)<0, C(i-1), D(i-1))` |

| E(i) | `=B(i)^2-2` |

| F(i) | `=C(i)^2-2` |

| G(i) | `=D(i)^2-2` |

| H(i) | `=E(i)*F(i)` |

| I(i) | `=ABS((C(i)-C(i-1))/C(i))*100` |

| J(i) | `=IF(I(i)<0.00001,"SI","NO")` |

**Fila de título (fila 25):** Mergeada A25:J25 — texto: `"MÉTODO DE BISECCIÓN  —  f(x) = x² − 2 = 0"`

**Fila de parámetros (fila 26):**

| Celda | Valor |

|-------|-------|

| A26 | `"Ecuación:"` |

| B26 | `"f(x) = x² - 2"` |

| D26 | `"Intervalo inicial:"` |

| E26 | `"[a₀, b₀] = [1, 2]"` |

| G26 | `"Tolerancia:"` |

| H26 | `"ε < 1×10⁻⁵ %"` |

---

### 4.2 REGULA FALSI (Hoja 2)

**Diferencia clave vs Bisección:** La fórmula de cₖ usa interpolación lineal en lugar de punto medio.

| Celda | Fórmula |

|-------|---------|

| C2 | `=B2-(E2*(D2-B2))/(G2-E2)` |

| C(i≥3) | `=B(i)-(E(i)*(D(i)-B(i)))/(G(i)-E(i))` |

El resto de las columnas (A, B, D, E, F, G, H, I, J) siguen exactamente el **mismo patrón** que Bisección.

**Fórmula canónica:**

```

c = a - f(a)·(b-a) / (f(b)-f(a))

equivalente a:

c = B(i) - E(i)*(D(i)-B(i))/(G(i)-E(i))

```

---

### 4.3 PUNTO FIJO (Hoja 3)

**g(x) del archivo:** `g(x) = (x + 2) / (x + 1)`

| Celda | Fórmula |

|-------|---------|

| A2 | `0` |

| B2 | `1` (x₀ hardcoded) |

| C2 | `=(B2+2)/(B2+1)` |

| B(i≥3) | `=C(i-1)` |

| C(i≥3) | `=(B(i)+2)/(B(i)+1)` |

| D(i≥3) | `=ABS((C(i)-B(i))/C(i))*100` |

| E(i≥3) | `=IF(D(i)<0.00001,"SI","NO")` |

---

### 4.4 AITKEN (Δ²) (Hoja 4)

**Estructura dual:** Dos tablas lado a lado. Columnas I–M: Punto Fijo auxiliar. Columnas A–D: Aitken acelerado.

**Tabla auxiliar de Punto Fijo (columnas I–M):**

| Celda | Fórmula |

|-------|---------|

| J2 | `1` (x₀) |

| K2 | `=(J2+2)/(J2+1)` |

| J(i≥3) | `=K(i-1)` |

| K(i≥3) | `=(J(i)+2)/(J(i)+1)` |

| L(i≥3) | `=ABS((K(i)-J(i))/K(i))*100` |

| M(i≥3) | `=IF(L(i)<0.00001,"SI","NO")` |

**Tabla Aitken (columnas A–D) — FÓRMULA Δ²:**

```

p̂ₖ = pₖ - (pₖ₊₁ - pₖ)² / (pₖ₊₂ - 2·pₖ₊₁ + pₖ)

```

| Celda | Fórmula |

|-------|---------|

| B2 | `=K2-(((K3-K2)^2)/(K4-2*K3+K2))` |

| B3 | `=K3-(((K4-K3)^2)/(K5-2*K4+K3))` |

| B4 | `=K4-(((K5-K4)^2)/(K6-2*K5+K4))` |

| C(i≥3) | `=ABS((B(i)-B(i-1))/B(i))*100` |

| D(i≥3) | `=IF(C(i)<0.00001,"SI","NO")` |

---

### 4.5 STEFFENSEN (Hoja 5)

**Arquitectura de 3 niveles apilados verticalmente:**

- Filas 1–3: Tabla Steffensen (columnas A–D)

- Filas 7–11: Tabla Aitken secundaria (columnas I–L)

- Filas 17–29: Tabla Punto Fijo base (columnas I–M)

**Steffensen (columnas A–D, usa Aitken como base):**

```

p̂ₖ = pₖ - (pₖ₊₁ - pₖ)² / (pₖ₊₂ - 2·pₖ₊₁ + pₖ)  — aplicado sobre los valores de Aitken

```

| Celda | Fórmula |

|-------|---------|

| B2 | `=J8-(((J9-J8)^2)/(J10-2*J9+J8))` |

| B3 | `=J9-(((J10-J9)^2)/(J11-2*J10+J9))` |

| C3 | `=ABS((B3-B2)/B3)*100` |

| D3 | `=IF(C3<0.00001,"SI","NO")` |

**Aitken (columnas I–L, filas 7–11):**

| Celda | Fórmula |

|-------|---------|

| J8 | `=K20-(((K21-K20)^2)/(K22-2*K21+K20))` |

| J9 | `=K21-(((K22-K21)^2)/(K23-2*K22+K21))` |

| J10 | `=K22-(((K23-K22)^2)/(K24-2*K23+K22))` |

| J11 | `=K23-(((K24-K23)^2)/(K25-2*K24+K23))` |

*(La tabla de Punto Fijo en filas 19+ alimenta los K20:K25)*

---

### 4.6 NEWTON-RAPHSON (Hoja 6)

**Fórmula:** `xₙ₊₁ = xₙ − f(xₙ) / f'(xₙ)`

| Celda | Fórmula |

|-------|---------|

| B2 | `1` (x₀) |

| C2 | `=B2^2-2` |

| D2 | `=2*B2` |

| E2 | `=B2-(C2/D2)` |

| B(i≥3) | `=E(i-1)` |

| C(i≥3) | `=B(i)^2-2` |

| D(i≥3) | `=2*B(i)` |

| E(i≥3) | `=B(i)-(C(i)/D(i))` |

| F(i≥3) | `=ABS((E(i)-B(i))/E(i))*100` |

| G(i≥3) | `=IF(F(i)<0.00001,"SI","NO")` |

> **Nota:** El error en fila 2 (k=0) **también se calcula**: `F2 = ABS((E2-B2)/E2)*100`

---

### 4.7 NEWTON MODIFICADO (Hoja 7)

**Fórmula:** `xₙ₊₁ = xₙ − [f(xₙ)·f'(xₙ)] / [(f'(xₙ))² − f(xₙ)·f''(xₙ)]`

**Diferencia clave:** f''(x) se almacena como **constante hardcoded** en celda `$B$9` (referencia absoluta).

| Celda | Fórmula/Valor |

|-------|--------------|

| B9 | `=2*1` (f''(x) = 2, hardcoded) |

| E(i) | `=$B$9` (referencia absoluta a f'') |

| F(i) | `=B(i)-((C(i)*D(i))/(D(i)^2-C(i)*E(i)))` |

| G(i) | `=ABS((F(i)-B(i))/F(i))*100` |

| H(i) | `=IF(G(i)<0.00001,"SI","NO")` |

---

### 4.8 NEWTON 2do ORDEN (Hoja 8)

**Fórmula:** `xₙ₊₁ = xₙ + (−f'(xₙ) + √((f'(xₙ))² − 2·f''(xₙ)·f(xₙ))) / f''(xₙ)`

| Celda | Fórmula |

|-------|---------|

| E2 | `2` (f''(x) hardcoded como valor) |

| F(i) | `=B(i)+((-D(i)+((D(i))^2-2*E(i)*C(i))^(1/2))/E(i))` |

---

### 4.9 CHEBYSHEV (Hoja 9)

**Fórmula:** `xₙ₊₁ = xₙ − (f/f') − [(f²·f'') / (2·(f')³)]`

| Celda | Fórmula/Valor |

|-------|--------------|

| B8 | `2` (f''(x) hardcoded) |

| E(i) | `=$B$8` |

| F(i) | `=B(i)-(C(i)/D(i))-(((C(i)^2)*(E(i)))/(2*(D(i))^3))` |

| G(i) | `=ABS((F(i)-B(i))/F(i))*100` |

| H(i) | `=IF(G(i)<0.00001,"SI","NO")` |

---

### 4.10 HALLEY (Hoja 10)

**Fórmula:** `xₙ₊₁ = xₙ − f / [f' − (f''·f)/(2·f')]`

| Celda | Fórmula/Valor |

|-------|--------------|

| B8 | `2` (f''(x) hardcoded) |

| E(i) | `=$B$8` |

| F(i) | `=B(i)-(C(i)/(D(i)-(E(i)*C(i))/(2*D(i))))` |

---

### 4.11 SUPER HALLEY (Hoja 11)

**Fórmula:** `xₙ₊₁ = xₙ − [2·(f')² − f·f''] / [2·((f')² − f·f'')] · (f/f')`

| Celda | Fórmula/Valor |

|-------|--------------|

| B7 | `2` (f''(x) hardcoded) |

| E(i) | `=$B$7` |

| F(i) | `=B(i)-(2*(D(i)^2)-C(i)*E(i))/(2*((D(i)^2)-C(i)*E(i)))*((C(i))/(D(i)))` |

---

### 4.12 OSTROWSKY (Hoja 12)

**Fórmula:** `xₙ₊₁ = xₙ − (f'/√(f'²−f·f'')) · (f/f')`

**Nota:** Empieza en fila 2 (encabezados) y fila 3 (datos k=0), no fila 1.

| Celda | Fórmula/Valor |

|-------|--------------|

| E(i) | `2` (f''(x) hardcoded como valor fijo, no referencia) |

| F(i) | `=B(i)-(D(i)/((D(i)^2-C(i)*E(i))^(1/2)))*(C(i)/D(i))` |

---

### 4.13 SECANTE (Hoja 13)

**Fórmula:** `xₙ₊₁ = xₙ − f(xₙ)·(xₙ−xₙ₋₁) / (f(xₙ)−f(xₙ₋₁))`

**Estructura especial:**

- Fila 2 (k=0): solo B2 y C2, sin xₖ₋₁, sin xₖ₊₁

- Fila 3 (k=1): B3=2 hardcoded, D3=B2, E3=C2, F3=fórmula Secante

- Filas 4+ usan IFERROR para robustez

| Celda | Fórmula |

|-------|---------|

| B2 | `1` (x₀ hardcoded) |

| C2 | `=B2^2-2` |

| B3 | `2` (x₁ hardcoded) |

| C3 | `=B3^2-2` |

| D3 | `=B2` |

| E3 | `=C2` |

| F3 | `=B3-(C3*(B3-D3)/(C3-E3))` |

| G3 | `=IFERROR(ABS((F3-B3)/F3)*100,0)` |

| H3 | `=IF(IFERROR(G3,0)<0.00001,"SI","NO")` |

| B(i≥4) | `=IFERROR(F(i-1),B(i-1))` |

| C(i≥4) | `=IFERROR(B(i)^2-2,0)` |

| D(i≥4) | `=IFERROR(B(i-1),B(i-1))` |

| E(i≥4) | `=IFERROR(C(i-1),0)` |

| F(i≥4) | `=IFERROR(B(i)-(C(i)*(B(i)-D(i))/(C(i)-E(i))),B(i))` |

---

### 4.14 VON MISES (Hoja 14)

**Fórmula:** `xₙ₊₁ = xₙ − f(xₙ) / f'(x₀)` — La derivada se evalúa **una sola vez** en x₀ y se usa como constante.

| Celda | Fórmula/Valor |

|-------|--------------|

| D(todas las filas) | `2` (f'(x₀) = 2·x₀ = 2·1 = 2, hardcoded) |

| E(i) | `=B(i)-(C(i)/D(i))` |

| F(i) | `=ABS((E(i)-B(i))/E(i))*100` |

| G(i) | `=IF(F(i)<0.00001,"SI","NO")` |

**Es el más lento:** necesita 18 iteraciones vs Newton-Raphson que necesita 4.

---

## 5. CRITERIO DE CONVERGENCIA UNIVERSAL

**Todos los métodos usan exactamente el mismo criterio:**

```excel

=IF(Error%_celda < 0.00001, "SI", "NO")

```

Esto equivale a: **Error relativo porcentual < 0.001%** → tolerancia de 1×10⁻⁵ %

El valor `0.00001` está hardcoded directamente en cada fórmula (no en celda de parámetro separada).

---

## 6. CÁLCULO DE ERROR — FÓRMULA UNIVERSAL

**Todos los métodos (excepto Von Mises en fila 2) usan:**

```excel

=ABS((x_nuevo - x_anterior) / x_nuevo) * 100

```

Es el **error relativo porcentual** respecto al valor nuevo.

Para la Secante se envuelve en IFERROR:

```excel

=IFERROR(ABS((F-B)/F)*100, 0)

```

---

## 7. ESTILOS Y FORMATO

### Bordes

- **Todos los bordes:** `thin` (delgado) en todas las celdas de datos

- Consistente en todas las hojas

### Fuente

- Fuente base: Calibri (por defecto de Excel)

- Tamaño: 11pt (default)

- Encabezados de columna: **no bold** (solo color de fondo los distingue)

- Títulos de método (fila mergeada): **bold=True**, color blanco

### Alineación

- Números: alineación por defecto (derecha para números, izquierda para texto)

- No se detectó alineación centrada explícita en celdas de datos

### Filas de título mergeadas

- **Alto de fila:** 17.25 pt (consistente en todas las hojas)

- **Merge range:** Cubre todas las columnas usadas por esa hoja

### Alternancia de colores en filas de datos

- Filas pares (k=0, k=2, k=4...): color `light2` (más claro)

- Filas impares (k=1, k=3, k=5...): color `light1` (header color)

- Los colores se asignan por posición de fila, no por valor de k

---

## 8. PATRONES DE REUTILIZACIÓN DE FÓRMULAS DE f(x) y f'(x)

**f(x) = x² - 2 en Excel:**

- Bisección/RF: `=celda^2-2`

- Newton-Raphson y derivados: `=B(i)^2-2`

**f'(x) = 2x en Excel:**

- Newton-Raphson: `=2*B(i)`

- Newton Modificado: `=2*(B(i))`

- Secante: no usa f'(x) — usa diferencias finitas

**f''(x) = 2 en Excel:**

- Newton Modificado: `=$B$9` (referencia absoluta a celda con valor `=2*1`)

- Newton 2do Orden: `2` (valor literal)

- Chebyshev: `=$B$8` (referencia absoluta a celda con valor `2`)

- Halley: `=$B$8` (referencia absoluta)

- Super Halley: `=$B$7` (referencia absoluta)

- Ostrowsky: `2` (valor literal en cada celda)

---

## 9. DIFERENCIAS IMPORTANTES ENTRE MÉTODOS

| Aspecto | Bisección | Regula Falsi | Newton-R | Secante | Von Mises |

|---------|-----------|--------------|----------|---------|-----------|

| Error en k=0 | ❌ No calcula | ❌ No calcula | ✅ Calcula desde k=0 | ❌ No en k=0 | ✅ Calcula desde k=0 |

| Fórmula xₖ₊₁ en columna | C | C | E | F | E |

| Parámetro f'' | No aplica | No aplica | No aplica | No aplica | No aplica |

| xₖ₊₁ depende de columnas | B, D | B, D, E, G | B, C, D | B, C, D, E | B, C, D |

---

## 10. RECOMENDACIONES DE IMPLEMENTACIÓN PARA EL GENERADOR

### Abstracción de funciones dinámicas

Cuando el usuario ingrese `f(x) = x^3 - 4x + 1`, el sistema debe reemplazar:

| En el Excel original | Sustitución dinámica |

|---------------------|---------------------|

| `=B(i)^2-2` | `=B(i)^3-4*B(i)+1` |

| `=2*B(i)` | `=3*B(i)^2-4` |

| `=$B$8` → 2 | `=$B$8` → f''(x) calculada por SymPy |

### Generador de fórmulas Excel desde expresiones SymPy

La clave del sistema es un **transpilador SymPy→Excel**:

```python

# Ejemplo:

sympy_expr = "x**3 - 4*x + 1"

excel_formula_row_i = "=B{i}^3-4*B{i}+1"

```

### Número de iteraciones por método

Basado en el archivo, estos son los rangos usados:

- Bisección: 22 filas de iteración (k=0 a k=21)

- Von Mises: 18 filas (el más lento)

- Newton-R: 4 filas (el más rápido con cuadrática)

- Steffensen/Aitken: 3-4 filas

**Recomendación:** Generar siempre 25 filas y usar IFERROR/condicionales para mostrar `""` cuando ya convergió.

---

## 11. RESUMEN DE FÓRMULAS DE CADA MÉTODO (REFERENCIA RÁPIDA)

| Método | Columna xₙ₊₁ | Fórmula Excel clave |

|--------|--------------|---------------------|

| Bisección | C | `=(B+D)/2` |

| Regula Falsi | C | `=B-(E*(D-B))/(G-E)` |

| Punto Fijo | C | `=g(B)` |

| Aitken | B | `=K-(((K_next-K)^2)/(K_next2-2*K_next+K))` |

| Newton-Raphson | E | `=B-(C/D)` |

| Newton Modificado | F | `=B-((C*D)/(D^2-C*E))` |

| Newton 2do Orden | F | `=B+((-D+((D)^2-2*E*C)^(1/2))/E)` |

| Chebyshev | F | `=B-(C/D)-(((C^2)*E)/(2*(D)^3))` |

| Halley | F | `=B-(C/(D-(E*C)/(2*D)))` |

| Super Halley | F | `=B-(2*(D^2)-C*E)/(2*((D^2)-C*E))*(C/D)` |

| Ostrowsky | F | `=B-(D/((D^2-C*E)^(1/2)))*(C/D)` |

| Secante | F | `=B-(C*(B-D)/(C-E))` |

| Von Mises | E | `=B-(C/D)` donde D es f'(x₀) constante |

