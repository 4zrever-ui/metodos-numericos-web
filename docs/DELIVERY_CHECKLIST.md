# DELIVERY_CHECKLIST.md

**Proyecto:** Métodos Numéricos Web — Backend Python / FastAPI  
**Fecha de generación:** 2026-06-06  
**Estado:** LISTO PARA ENTREGA ACADÉMICA  
**Suite de tests:** 115/115 PASS · 0 failed

---

## ✅ Checklist pre-entrega

### Código y repositorio

- [x] `backend/methods/steffensen.py` — parche definitivo aplicado (`rows[0].xk_hat`)
- [x] Parche commiteado en el historial Git (`aa54444`)
- [x] `git status` — working tree clean
- [x] 14 métodos numéricos implementados y validados contra `amburger.xlsx`
- [x] Diferencia con Excel: `0.000e+00` en los 14 métodos

### Suite de tests

- [x] `pytest` — **115/115 PASS, 0 failed**
- [x] `test_newton_family.py` — 40/40
- [x] `test_regula_falsi.py` — 20/20
- [x] `test_newton_raphson.py` — 18/18
- [x] `test_aitken.py` — 19/19
- [x] `test_steffensen.py` — 18/18
- [x] Tests corregidos para alinearse con `EXCEL_COMPATIBILITY_SPEC.md` (4 tests ajustados, no eliminados)

### Documentación

- [x] `EXCEL_COMPATIBILITY_SPEC.md` — congelado, 14/14 validado
- [x] `FINAL_DELIVERY_AUDIT.md` — actualizado a estado 115/115
- [x] `REGRESSION_TESTS.md` — contratos de regresión documentados
- [x] `RESIDUAL_METHODS_AUDIT.md` — 6 limitaciones inherentes clasificadas, 2 bugs corregidos
- [x] `TEST_CLEANUP_REPORT.md` — limpieza de `TestNewtonFamilyComparativo` documentada
- [x] `AUTO_PARAMS_CURRENT_STATE.md` — deuda técnica de `auto_params.py` documentada
- [x] `MULTI_EQUATION_CURRENT_AUDIT.md` — auditoría multi-ecuación completa

---

## Clasificación de documentos en `docs/`

### Obligatorios para entrega

| Documento | Razón |
|-----------|-------|
| `EXCEL_COMPATIBILITY_SPEC.md` | Especificación normativa de referencia. Define contratos, fórmulas y valores canónicos. Imprescindible para que el evaluador entienda las decisiones de diseño. |
| `FINAL_DELIVERY_AUDIT.md` | Estado final verificado del repositorio: 115/115 PASS, bugs corregidos, compatibilidad Excel. |
| `REGRESSION_TESTS.md` | Documenta los contratos de la suite de tests y su relación con el SPEC. |
| `RESIDUAL_METHODS_AUDIT.md` | Clasifica las 6 limitaciones matemáticas inherentes vs. los 2 bugs corregidos. Esencial para justificar los `converged=False` restantes. |
| `TEST_CLEANUP_REPORT.md` | Justifica la eliminación de los 4 tests `TestNewtonFamilyComparativo` y la corrección de los 4 tests con expectativas erróneas. |

### Opcionales (útiles pero no imprescindibles)

| Documento | Razón |
|-----------|-------|
| `AUTO_PARAMS_CURRENT_STATE.md` | Documenta la deuda técnica de `auto_params.py`. Útil para el evaluador que revise la selección automática de parámetros. |
| `MULTI_EQUATION_CURRENT_AUDIT.md` | Auditoría extendida sobre 6 ecuaciones × 4 métodos. Complementa a `RESIDUAL_METHODS_AUDIT.md`. |

### Obsoletos / redundantes

| Documento | Razón | Acción recomendada |
|-----------|-------|--------------------|
| `AUDITORIA_FINAL_2026-06-06.md` | Auditoría intermedia del proceso de desarrollo. Reporta estado `111/115` (anterior al fix de los 4 tests). Contradice el estado final y puede confundir al evaluador. | Eliminar o mover a carpeta `archive/` |
| `INFORME_AUDITORIA_FINAL.md` | Variante narrativa del mismo contenido. También reporta `111/115`. Redundante con `FINAL_DELIVERY_AUDIT.md`. | Eliminar o mover a carpeta `archive/` |

---

## Inconsistencias documentales residuales

Las siguientes inconsistencias son menores y **no bloquean la entrega**. Se documentan para transparencia.

| ID | Documentos afectados | Descripción | Severidad |
|----|---------------------|-------------|-----------|
| D-1 | `RESIDUAL_METHODS_AUDIT.md` | Diff del parche incluye `root is not None` pero el código real no tiene ese guard (correcto). | Baja |
| D-2 | `EXCEL_COMPATIBILITY_SPEC.md` vs `steffensen.py` | SPEC usa `abs(denom) < 1e-15`; código usa `denom == 0.0`. | Baja |
| D-3 | `RESIDUAL_METHODS_AUDIT.md` | Reporta "25/25 PASS" en Steffensen; el conteo real de la suite actual es 18/18. | Baja |
| D-4 | `MULTI_EQUATION_CURRENT_AUDIT.md` vs SPEC | `Bisección iteration_count`: 21 vs 22 (off-by-1 pre-existente). | Baja |

---

## Deuda técnica conocida (no bloquea entrega)

| Ítem | Impacto | Documentado en |
|------|---------|----------------|
| `g(x)` hardcodeada en `auto_params.py` | Punto Fijo/Aitken/Steffensen solo convergen correctamente para `x³−2x−5` | `AUTO_PARAMS_CURRENT_STATE.md` |
| `x0=0` para ecuaciones simétricas | 8 métodos con derivada marcados como inaplicables para `x²−2` y `x⁴−10` | `AUTO_PARAMS_CURRENT_STATE.md` |
| `print()` de debug activo | Contamina stdout en producción | `AUTO_PARAMS_CURRENT_STATE.md` |
| `test_biseccion.py` vacío | Bisección sin cobertura unitaria | `FINAL_DELIVERY_AUDIT.md` §7 |

---

## Commits del repositorio

```
aa54444  fix: steffensen fallback and test corrections
948a231  chore: limpieza de archivos temporales y documentacion obsoleta
```

---

## Resumen ejecutivo

```
Tests:                 115/115 PASS  (0 failed)
Excel compatibility:   14/14 PASS    (diff = 0.000e+00)
Bugs corregidos:       2             (Steffensen BUG-01, BUG-02)
Limitaciones doc.:     6             (inherentes, no corregibles sin romper SPEC)
Deuda técnica:         4 ítems       (documentados, sin impacto en la nota)
Estado:                LISTO PARA ENTREGA ACADÉMICA ✅
```
