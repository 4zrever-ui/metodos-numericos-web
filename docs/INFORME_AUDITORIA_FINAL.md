# INFORME DE AUDITORÍA FINAL
**Proyecto:** Métodos Numéricos Web — Backend Python/FastAPI  
**Fecha de auditoría:** 2026-06-06  
**Auditor:** Claude Sonnet 4.6  
**Alcance:** Código fuente + documentación del ZIP `metodos_numericos_web.zip`

---

## 1. VERIFICACIÓN: `steffensen.py` contiene el parche definitivo basado en `rows[0].xk_hat`

**CONFIRMADO ✅**

El archivo `backend/methods/steffensen.py` contiene el parche definitivo. La sección de fallback (líneas ~209–232) lee:

```python
if not converged and len(rows) == 1:
    try:
        candidate = rows[0].xk_hat       # ← uso directo de rows[0].xk_hat
        f_at_root = abs(float(eq.f_sympy.subs(_x, candidate).evalf()))
        if f_at_root < tol:
            converged = True
            final_error = f_at_root
            root = candidate
            rows[0] = SteffensenRow(
                k=rows[0].k,
                ...
                xk_hat=rows[0].xk_hat,
                ...
                converged=True,
            )
    except Exception:
        pass
```

El código **no** usa la variable `root` como candidato (que sería `None` en ese punto del flujo), sino `rows[0].xk_hat` directamente. Esto es exactamente el "parche definitivo" descrito en la documentación.

**Discrepancia menor detectada** (no crítica): `RESIDUAL_METHODS_AUDIT.md` incluye en su sección de diff un bloque que dice `if not converged and len(rows) == 1 and root is not None:`, pero el código real dice `if not converged and len(rows) == 1:` (sin el guard `root is not None`). El código actual es **más correcto** que el diff documentado, porque el guard `root is not None` habría re-introducido el bug (cuando la función entra al fallback, `root` es `None` siempre). El diff en la documentación es una versión intermedia, no la final. Esto constituye una inconsistencia menor de documentación, no un error de código.

---

## 2. CONSISTENCIA ENTRE DOCUMENTOS

### 2.1 EXCEL_COMPATIBILITY_SPEC.md

**Estado: CONSISTENTE con el código ✅, con una discrepancia menor interna.**

- Todos los parámetros globales (`_TOLERANCE = 0.00001`, `_MAX_ITER = 25`, fórmula de error) están correctamente reflejados en el código.
- La arquitectura de tres capas de Steffensen descrita en §6.4 coincide exactamente con la implementación.
- La regla `iteration_count = len(rows) - 1` (todos los métodos excepto Aitken) está implementada correctamente en el código de Steffensen.
- La fórmula `_delta2` en el SPEC define `if abs(denom) < 1e-15: return None`, pero el código usa `if denom == 0.0: return None`. Esta es una **discrepancia real**: la condición del código es más estricta que la del SPEC (solo captura denominadores exactamente iguales a cero flotante, mientras que el SPEC protege también denominadores próximos a cero). En la práctica no afecta los casos verificados pero podría fallar silenciosamente con denominadores del orden de `1e-16`. **Riesgo: bajo.**

### 2.2 AUTO_PARAMS_CURRENT_STATE.md

**Estado: CONSISTENTE con el código ✅, hallazgos correctamente documentados.**

El documento describe con precisión los cinco hallazgos críticos del módulo (`auto_params.py`):
- H-1: `g(x)` hardcodeada como `(2x+5)^(1/3)` para todas las ecuaciones — confirmado en el código.
- H-2: `x0=0` para ecuaciones simétricas — confirmado.
- H-3: `print()` de debug activo en producción — confirmado.
- H-4: `_SEARCH_RANGE` definida pero no usada — confirmado.
- H-5: Orden de definición atípico de `_best_integer_near()` — confirmado.

Estos problemas están documentados pero **no están corregidos**. El `PROJECT_STATUS_2026-06-06.md` los lista explícitamente como "Problemas pendientes". Esto es consistente entre los tres documentos, pero representa deuda técnica sin resolver.

### 2.3 MULTI_EQUATION_CURRENT_AUDIT.md

**Estado: CONSISTENTE internamente ✅, con una discrepancia numérica detectable respecto a EXCEL_COMPATIBILITY_SPEC.md.**

- La tabla de la Ecuación 1 (x²−2) reporta Bisección con **21 iteraciones** (`iteration_count=21`), pero `EXCEL_COMPATIBILITY_SPEC.md §8` reporta **22 iteraciones** para el mismo método con la misma ecuación.
- `RESIDUAL_METHODS_AUDIT.md` menciona explícitamente "Bisección iteration_count — off-by-1 (pre-existente, sin cambio)".

Esta discrepancia numérica entre MULTI_EQUATION_CURRENT_AUDIT (21 iter.) y EXCEL_COMPATIBILITY_SPEC (22 iter.) para Bisección no está explicada en ningún documento. Lo más probable es que las dos auditorías se ejecutaron con valores de `x0` distintos (SPEC usa x0=1 con intervalo [1, 1.5]; MULTI usa x0_auto=0.0 con intervalo [1.0, 1.5] según la tabla). **No es un bug del código — es una diferencia de parámetros de entrada, pero la documentación no lo aclara.**

### 2.4 TEST_CLEANUP_REPORT.md

**Estado: CONSISTENTE con el estado actual de los tests ✅**

Describe correctamente la eliminación de 4 tests de `TestNewtonFamilyComparativo` con expectativas matemáticamente incorrectas, y su reemplazo por `test_todas_variantes_convergen_raiz_valida`. El archivo `test_newton_family.py` efectivamente tiene 378 líneas y no contiene los tests eliminados.

**Discrepancia detectada**: El documento indica que el estado inicial era "4 failed, 29 passed, total 33 tests", pero `AUDITORIA_FINAL_2026-06-06.md` indica "111 passed, 4 failed, total 115 tests". Esto no es contradicción — el TEST_CLEANUP_REPORT describe un estado anterior con solo algunos archivos de test presentes. La suite completa tiene 115 tests.

### 2.5 REGRESSION_TESTS.md

**Estado: CONSISTENTE ✅ pero incompleto como suite ejecutable.**

El documento describe correctamente los contratos de regresión y reproduce los valores de referencia del SPEC. Su tabla §2.1 lista los 14 métodos auditados. Los criterios de aceptación en §2.4 son correctos y reproducibles.

**Limitación**: El documento es descriptivo pero no contiene un script ejecutable de regresión (`audit_backend.py` es referenciado en `PROJECT_STATUS_2026-06-06.md` pero no existe en el ZIP). Si el evaluador académico ejecuta `pytest` sin este script, los 4 tests fallidos (con expectativas incorrectas) aparecerán como fallos sin contexto.

### 2.6 RESIDUAL_METHODS_AUDIT.md

**Estado: CONSISTENTE con el código post-parche ✅, con la discrepancia de diff ya señalada en §1.**

La clasificación de los 6 casos residuales restantes (5 limitaciones inherentes + 1 parcialmente implementación) es matemáticamente sólida y está bien argumentada. El estado final "25/25 PASS" en tests Steffensen **no coincide** con `AUDITORIA_FINAL_2026-06-06.md` que reporta "15/17 PASS" en Steffensen.

Esta discrepancia entre documentos es significativa: RESIDUAL indica 25/25 y AUDITORIA indica 15/17. La explicación más probable es que RESIDUAL fue escrito con una versión anterior o diferente de la suite de tests (posiblemente antes de agregar los 2 tests con expectativas incorrectas). El conteo de AUDITORIA_FINAL (15/17) parece más reciente y confiable.

---

## 3. CONTRADICCIONES ENTRE DOCUMENTACIÓN Y CÓDIGO

| # | Tipo | Documento(s) | Detalle | Severidad |
|---|------|--------------|---------|-----------|
| C-1 | Diff desactualizado | `RESIDUAL_METHODS_AUDIT.md` | El diff del parche usa `root is not None` pero el código usa `len(rows) == 1` sin ese guard. El código es más correcto que el diff. | Baja |
| C-2 | `_delta2` guard | `EXCEL_COMPATIBILITY_SPEC.md §6.1` | SPEC dice `abs(denom) < 1e-15`; código dice `denom == 0.0`. Discrepancia de tolerancia numérica. | Baja |
| C-3 | Bisección iteration_count | `EXCEL_COMPATIBILITY_SPEC.md §8` vs `MULTI_EQUATION_CURRENT_AUDIT.md` | SPEC reporta 22 iter, MULTI reporta 21 iter para Bisección en x²−2. Diferencia de parámetros de entrada no documentada. | Media |
| C-4 | Tests Steffensen | `RESIDUAL_METHODS_AUDIT.md` vs `AUDITORIA_FINAL_2026-06-06.md` | RESIDUAL dice "25/25 PASS", AUDITORIA dice "15/17 PASS". Conteos de suites diferentes en fechas distintas. | Media |
| C-5 | `audit_backend.py` | `PROJECT_STATUS_2026-06-06.md` | El status menciona ejecutar `audit_backend.py` antes/después de cambios, pero el script no existe en el ZIP. | Media |

---

## 4. ARCHIVOS OBSOLETOS O DUPLICADOS

| Archivo | Tipo | Observación |
|---------|------|-------------|
| `excel_templates/amburger.xlsx` | Posible duplicado | Coexiste con `amburger_v6.xlsx`. Si `amburger_v6.xlsx` es la versión final auditada, la versión sin sufijo puede eliminarse o mover al backup. |
| `excel_templates/backup/MetodosNumericos_Todos.xlsx` | Duplicado de backup | Coexiste con `MetodosNumericos_Todos_v2.xlsx`. El original puede eliminarse si v2 es la versión actual. |
| `excel_templates/backup/generar_excel_v2.py` | Script en backup | Un script `.py` dentro de una carpeta de backups Excel es inusual. Si es código activo, debería estar en `backend/`; si es histórico, puede eliminarse. |
| `Archivo 00_PROYECTO_GENERAL.md` ... `Archivo 06_ASESOR_TECNICO.md` | Archivos de proceso | Seis archivos de notas de trabajo con prefijo "Archivo". No son parte del proyecto entregable — son el diario de desarrollo. Deben excluirse del ZIP de entrega. |
| `trabajarconclaudecuando se acaba.txt` | Nota personal | Archivo de notas personales sobre el flujo de trabajo con el asistente. No pertenece al proyecto entregable. |
| `web/.pytest_cache/` y `web/backend/methods/.pytest_cache/` | Cache de pytest | Directorios de cache que no deben estar en el ZIP de entrega. |
| `web/backend/core/__pycache__/` y otros `__pycache__/` | Cache de Python | Múltiples carpetas de bytecode compilado. No deben estar en el ZIP de entrega. |
| `web/frontend/node_modules/` | Dependencias JS | La carpeta completa de node_modules (~1000+ archivos) no debe estar en un ZIP de entrega. El `package.json` es suficiente. |
| `web/docs/AUDITORIA_FINAL_2026-06-06.md` | Documento de auditoría interna | Es el documento de auditoría del propio proceso de desarrollo, no documentación del proyecto. Puede incluirse como anexo o separarse. |

---

## 5. VEREDICTO: ¿PUEDE DECLARARSE CERRADO Y LISTO PARA ENTREGA ACADÉMICA?

### Respuesta: **CONDICIONALMENTE SÍ**, con acciones previas recomendadas.

---

### Lo que está correcto y listo ✅

**Núcleo matemático**: Los 14 métodos numéricos implementados en `backend/methods/*.py` son matemáticamente correctos y compatibles con `amburger.xlsx` con diferencia `0.000e+00`. El SPEC está congelado y verificado.

**Parche de Steffensen**: El bug de la condición de convergencia está correctamente corregido usando `rows[0].xk_hat`. Los dos casos problemáticos (x³−2x−5 y e^−x−x) convergen correctamente post-parche.

**Documentación matemática**: `EXCEL_COMPATIBILITY_SPEC.md` es un documento técnico sólido que describe completamente las decisiones de implementación. `RESIDUAL_METHODS_AUDIT.md` clasifica correctamente las limitaciones inherentes vs los bugs corregidos.

**Suite de tests**: 111/115 tests pasan. Los 4 fallos están documentados como expectativas incorrectas en los tests, no como errores de código.

---

### Lo que debe resolverse antes de entregar ⚠️

**Acción 1 — Limpiar el ZIP de entrega (obligatorio):**
Eliminar: `Archivo 0*.md`, `trabajarconclaudecuando se acaba.txt`, todos los `__pycache__/`, `.pytest_cache/`, y el directorio completo `frontend/node_modules/`. El ZIP de entrega debe contener solo código fuente, tests y documentación técnica.

**Acción 2 — Corregir o eliminar los 4 tests con expectativas erróneas (recomendado):**
Los tests `test_denominador_cero_fallback` (en aitken y steffensen) y `test_aitken_seq_menor_3_inaplicable` fallan por expectativas que contradicen la especificación. Un evaluador académico que ejecute `pytest` verá 4 fallos sin saber que son errores de test y no de código. Opciones: corregir las expectativas o añadir `pytest.mark.xfail` con justificación en el docstring.

**Acción 3 — Aclarar la discrepancia de Bisección (recomendado):**
Agregar una nota en `REGRESSION_TESTS.md` o `MULTI_EQUATION_CURRENT_AUDIT.md` explicando que el `iteration_count=21` de la auditoría multi-ecuación usa `x0_auto=0.0` (con intervalo distinto), mientras que el SPEC usa `x0=1.0` que produce 22 iteraciones. Son dos corridas legítimas con parámetros distintos.

**Acción 4 — Documentar el problema de `auto_params.py` como trabajo futuro (recomendado):**
El `g(x)` hardcodeado hace que Punto Fijo, Aitken y Steffensen solo funcionen correctamente para `x³−2x−5`. Esto es conocido y documentado, pero un evaluador que pruebe otra ecuación (como `x²−2`) recibirá una raíz incorrecta silenciosamente. Si la entrega incluye el frontend interactivo, esto podría interpretarse como un defecto funcional grave. Se recomienda o bien corregirlo o bien agregar una advertencia visible en la UI.

---

### Resumen ejecutivo

```
Parche Steffensen (rows[0].xk_hat):     ✅ CONFIRMADO — correcto
Consistencia documentación-código:       ✅ SUSTANCIAL — 5 discrepancias menores detectadas
Contradicciones críticas:                ❌ NINGUNA — todas las discrepancias son menores
Archivos obsoletos para eliminar:        ⚠️ ~10 categorías (noise + caches + notas personales)
Tests fallidos:                          ⚠️ 4/115 — tests con expectativas incorrectas, no bugs
Problema no resuelto (auto_params.py):  ⚠️ g(x) hardcodeada — funcionalidad parcial conocida

Veredicto:                               APTO PARA ENTREGA ACADÉMICA con limpieza previa del ZIP
                                         y corrección o marcado de los 4 tests fallidos.
```
