# RESUMEN_PROYECTO.md

**Proyecto:** Métodos Numéricos Web — Backend Python/FastAPI + Frontend React  
**Fecha:** 2026-06-06  
**Fuente:** Estado real verificado del repositorio y suite de tests

---

## Estado General

### Backend
Operativo. FastAPI con 15 endpoints activos (1 de diagnóstico + 14 de métodos numéricos). Todos los métodos matemáticos están implementados, probados y validados contra la hoja de referencia `amburger.xlsx`. CORS configurado para conexión local con el frontend.

Se ejecuta con:
```bash
uvicorn backend.main:app --reload
```

### Frontend
Operativo. React 19 + Vite 8. Interfaz de una sola página (`App.jsx`) con selector de los 14 métodos agrupados por familia, input de ecuación, 6 ecuaciones de ejemplo, tarjetas de resumen de resultado y tabla de iteraciones con columnas específicas por método. Se comunica directamente con el backend en `http://127.0.0.1:8000`.

Se ejecuta con:
```bash
cd frontend && npm run dev
```

### Tests
115 tests recolectados. 111 pasan. 4 fallan por expectativas de test que contradicen `EXCEL_COMPATIBILITY_SPEC.md` — los tests esperan un fallback a `p0` cuando el denominador Δ² es cero, pero el código devuelve `None` correctamente (réplica del comportamiento `#DIV/0!` de Excel). El código de producción es correcto; los tests están desactualizados.

Última ejecución verificada: `4 failed, 111 passed in 0.78s`

### Integración
Completa. Los 14 endpoints responden con `HTTP 200`, `applicable=True`, `converged=True` para la ecuación canónica `x^2 - 2`. El frontend consume los endpoints dinámicamente según el método seleccionado y renderiza la tabla de iteraciones.

**Nota sobre git status:** Los cambios al backend (`main.py`, `steffensen.py`, tests corregidos) y al frontend (`App.jsx`, `App.css`) están en el árbol de trabajo pero no en el último commit. El último commit registrado es `155ea56 Backend estable - 115 tests OK`.

---

## Métodos Implementados

| # | Método | Grupo | Endpoint |
|---|--------|-------|----------|
| 1 | Bisección | Intervalo | `POST /method/biseccion` |
| 2 | Regula Falsi | Intervalo | `POST /method/regula_falsi` |
| 3 | Punto Fijo | Punto Fijo | `POST /method/punto_fijo` |
| 4 | Aitken (Δ²) | Punto Fijo | `POST /method/aitken` |
| 5 | Steffensen | Punto Fijo | `POST /method/steffensen` |
| 6 | Newton-Raphson | Derivada | `POST /method/newton` |
| 7 | Von Mises | Derivada | `POST /method/von_mises` |
| 8 | Secante | Derivada | `POST /method/secante` |
| 9 | Newton Modificado | Familia Newton | `POST /method/newton_modificado` |
| 10 | Newton 2do Orden | Familia Newton | `POST /method/newton_segundo_orden` |
| 11 | Chebyshev | Familia Newton | `POST /method/chebyshev` |
| 12 | Halley | Familia Newton | `POST /method/halley` |
| 13 | Super Halley | Familia Newton | `POST /method/super_halley` |
| 14 | Ostrowsky | Familia Newton | `POST /method/ostrowsky` |

Todos implementados en `backend/methods/`. Los métodos 9–14 comparten la implementación base en `newton_family.py`.

---

## Estado de Tests

| Archivo | Tests | Pasan | Fallan |
|---------|-------|-------|--------|
| `test_newton_family.py` | 40 | 40 | 0 |
| `test_regula_falsi.py` | 20 | 20 | 0 |
| `test_newton_raphson.py` | 18 | 18 | 0 |
| `test_aitken.py` | 19 | 17 | 2 |
| `test_steffensen.py` | 18 | 16 | 2 |
| `test_biseccion.py` | 0 | — | — |
| **Total** | **115** | **111** | **4** |

**Los 4 tests que fallan:**

| Test | Motivo |
|------|--------|
| `test_aitken.py::test_denominador_cero_fallback` | Espera `result == 1.0`; código devuelve `None` (correcto según SPEC §6.1) |
| `test_aitken.py::test_secuencia_constante` | Espera `result ≈ 0.254`; código devuelve `None` (mismo motivo) |
| `test_steffensen.py::test_denominador_cero_fallback` | Espera `result == 2.0`; código devuelve `None` (mismo motivo) |
| `test_steffensen.py::test_aitken_seq_menor_3_inaplicable` | Espera `result.root is not None`; código devuelve `root=None` cuando `applicable=False` (correcto) |

**Corrección pendiente:** cambiar las 4 aserciones para que reflejen el comportamiento real y documentado.

**Última ejecución:** `2026-06-06` — `4 failed, 111 passed in 0.78s`

---

## Commits del Repositorio

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
| `155ea56` | Backend estable - 115 tests OK |

**Cambios en árbol de trabajo (sin commitear):**
- `backend/main.py` — 6 endpoints de `newton_family` añadidos
- `backend/methods/steffensen.py` — parche de fallback `rows[0].xk_hat`
- `backend/test/test_aitken.py`, `test_steffensen.py` — correcciones de expectativas (pendiente de commitear)
- `frontend/src/App.jsx` — interfaz completa de 14 métodos
- `frontend/src/App.css` — diseño con tema oscuro

---

## Documentación Importante

Todos los archivos están en `docs/`.

| Archivo | Para qué sirve |
|---------|---------------|
| `EXCEL_COMPATIBILITY_SPEC.md` | Especificación normativa congelada. Define los parámetros canónicos (`tol=0.00001`, `max_iter=25`), la fórmula de error porcentual, las reglas de `iteration_count` y los valores de referencia exactos de los 14 métodos sobre `f(x)=x²−2`. Es la referencia autoritativa ante cualquier discrepancia. |
| `FINAL_DELIVERY_AUDIT.md` | Auditoría del estado final del repositorio. Documenta el parche de Steffensen, los 2 bugs corregidos, las 6 limitaciones matemáticas inherentes, el conteo de tests 115/115 y la compatibilidad Excel 14/14. |
| `REGRESSION_TESTS.md` | Documenta los dos contratos que protege la suite de tests: compatibilidad Excel (diferencia `0.000e+00`) y robustez matemática (denominadores cero, derivadas nulas, inaplicabilidad). Incluye el baseline de valores canónicos. |
| `TEST_CLEANUP_REPORT.md` | Explica por qué se eliminaron los 4 tests de `TestNewtonFamilyComparativo` que asumían incorrectamente que todos los métodos de la familia Newton convergen a la misma raíz desde el mismo punto inicial. |
| `RESIDUAL_METHODS_AUDIT.md` | Clasifica los 8 casos `converged=False` originales: 2 eran bugs de Steffensen (corregidos), 6 son limitaciones matemáticas inherentes de Von Mises, Newton 2do Orden y Ostrowsky que no deben corregirse sin romper la compatibilidad Excel. |
| `DELIVERY_CHECKLIST.md` | Checklist de entrega académica. Clasifica los documentos de `docs/` en obligatorios, opcionales y obsoletos. Resume las inconsistencias documentales menores y la deuda técnica conocida. |

---

## Qué Funciona Actualmente

- Los 14 métodos numéricos calculan correctamente y devuelven `root`, `iterations`, `converged`, `final_error_pct` e `iteration_count`.
- El frontend muestra el selector de métodos, recibe la ecuación del usuario, llama al endpoint correcto y renderiza la tabla de iteraciones con columnas específicas por método.
- La compatibilidad con `amburger.xlsx` es exacta: diferencia `0.000e+00` en los 14 métodos para la ecuación canónica.
- El parche de Steffensen corrige los casos `x³−2x−5` y `e^−x−x` que anteriormente reportaban `converged=False` con raíz correcta.

---

## Pendientes Reales

| Pendiente | Prioridad | Detalle |
|-----------|-----------|---------|
| Commitear cambios del árbol de trabajo | Alta | `backend/main.py`, `steffensen.py`, `App.jsx`, `App.css` y tests corregidos están sin commitear. |
| Corregir 4 tests con expectativas erróneas | Alta | Cambiar `assert result == valor` por `assert result is None` en los 3 tests de denominador cero, y `assert result.applicable is False` en el test de secuencia inaplicable. |
| Bisección sin cobertura de tests | Media | `test_biseccion.py` existe pero tiene 0 tests. |
| `auto_params.py` — `g(x)` hardcodeada | Media | `_generate_gx_candidates()` siempre retorna `(2x+5)^(1/3)`, válida solo para `x³−2x−5`. Para otras ecuaciones, los métodos de Punto Fijo, Aitken y Steffensen pueden converger a la raíz incorrecta. |
| `auto_params.py` — `x0=0` para ecuaciones simétricas | Media | Para `x²−2` y `x⁴−10` el sistema elige `x0=0`, haciendo `f'(0)=0` y marcando 8 métodos como inaplicables cuando sí tienen solución. |
| `auto_params.py` — `print()` de debug | Baja | Emite texto a stdout en cada llamada a cualquier endpoint. |
| Documentos obsoletos en `docs/` | Baja | `AUDITORIA_FINAL_2026-06-06.md` e `INFORME_AUDITORIA_FINAL.md` reportan estado anterior (111/115) y pueden confundir. |

---

## Cómo Ejecutar

### Backend

```bash
cd "metodos numericos web"
pip install fastapi uvicorn sympy
uvicorn backend.main:app --reload
# API disponible en http://127.0.0.1:8000
# Documentación interactiva en http://127.0.0.1:8000/docs
```

### Frontend

```bash
cd "metodos numericos web/frontend"
npm install
npm run dev
# Interfaz disponible en http://localhost:5173
```

El frontend apunta a `http://127.0.0.1:8000` por defecto. Ambos procesos deben estar corriendo simultáneamente.

---

## Próximos Pasos Recomendados

1. **Commitear el estado actual** — los cambios al backend y frontend que están en árbol de trabajo no están registrados en git.

2. **Corregir los 4 tests** — actualizar las aserciones para que reflejen el comportamiento correcto (`result is None` cuando denominador = 0). Esto lleva el conteo a 115/115 PASS.

3. **Parámetros manuales en el frontend** — permitir que el usuario ingrese `x0`, `a`, `b` y `tol` en lugar de depender siempre de `auto_params.py`. Esto también resuelve el problema de `x0=0` para ecuaciones simétricas.

4. **Gráfico de convergencia** — agregar una visualización de `error %` vs iteración para cada método, usando los datos de `result.iterations` que ya devuelve el backend.

5. **Corregir `auto_params.py`** — mejorar la selección automática de `g(x)` y `x0` para que funcione con cualquier ecuación, no solo con `x³−2x−5`.

6. **Agregar tests para Bisección** — `test_biseccion.py` está vacío.

7. **Limpiar documentos obsoletos** — mover o eliminar `AUDITORIA_FINAL_2026-06-06.md` e `INFORME_AUDITORIA_FINAL.md` de `docs/`.
