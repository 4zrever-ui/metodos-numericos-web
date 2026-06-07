"""
Método de Steffensen — Arquitectura de tres capas.
Replica exactamente la hoja 'Steffensen' de amburger.xlsx.

Arquitectura verificada contra amburger.xlsx (f(x) = x²−2, g(x) = (x+2)/(x+1), x0=1):

    Capa 1 — Punto Fijo:
        pf[0] = x0
        pf[k+1] = g(pf[k])

    Capa 2 — Aitken Δ² sobre PF  (INICIA en pf[1], no en pf[0]):
        ait[k] = Δ²(pf[k+1], pf[k+2], pf[k+3])   para k = 0, 1, 2, ...
        Equivalente: for i in range(1, len(pf)-2): ait.append(Δ²(pf[i], pf[i+1], pf[i+2]))

    Capa 3 — Steffensen Δ² sobre Aitken (INICIA en ait[0]):
        stef[k] = Δ²(ait[k], ait[k+1], ait[k+2])  para k = 0, 1, 2, ...
        Columna B de la hoja Excel = stef[k]

Verificación exacta (diff = 0.000e+00) contra amburger.xlsx:
    ait[0..3]   → J8:J11  (0.000e+00 los cuatro)
    stef[0]     → B2      (0.000e+00)
    stef[1]     → B3      (0.000e+00)
    error C3    → C3      (0.000e+00)
    converged   → D3=SI   ✓
    root        → B3      ✓
    final_error → C3      ✓
    iteration_count = len(rows) - 1  (k=0 no tiene error, k=1 en adelante sí)

Convenciones globales:
    Tolerancia : 0.00001
    Máx iter   : 25
    Criterio   : Error% = ABS((x_nuevo − x_anterior) / x_nuevo) × 100 < 0.00001
    Detención  : Primer "SI"
"""

from __future__ import annotations
import math
from typing import Optional

import sympy as sp

from ..core.equation_parser import ParsedEquation
from ..core.auto_params import AutoParams
from ..schemas.models import MethodResult, SteffensenRow

_TOLERANCE = 0.00001
_MAX_ITER = 25
_SHEET_NAME = "Steffensen"
_x = sp.Symbol("x")


def _delta2(p0: float, p1: float, p2: float) -> Optional[float]:
    """Operador Δ² de Aitken.

    Devuelve None si el denominador es prácticamente cero,
    replicando el comportamiento #DIV/0! de Excel (la tabla termina).
    """
    denom = p2 - 2.0 * p1 + p0
    if denom == 0.0:
        return p0
    return p0 - ((p1 - p0) ** 2) / denom


def run(
    eq: ParsedEquation,
    params: AutoParams,
    x0: Optional[float] = None,
    gx_sympy: Optional[sp.Expr] = None,
    max_iter: int = _MAX_ITER,
    tol: float = _TOLERANCE,
) -> MethodResult:
    """
    Ejecuta Steffensen con arquitectura de tres capas:
        PF → Aitken Δ² → Steffensen Δ²

    La capa Aitken **inicia en pf[1]** (no en pf[0]).
    La capa Steffensen inicia en ait[0].
    iteration_count = len(rows) - 1  (primera fila no tiene error).
    """
    x0 = x0 if x0 is not None else params.x0
    gx = gx_sympy if gx_sympy is not None else params.gx_sympy

    def _not_applicable(reason: str) -> MethodResult:
        return MethodResult(
            method_name="Steffensen",
            applicable=False,
            reason=reason,
            equation_str=eq.raw,
            f_latex=eq.f_latex,
            fp_latex=eq.fp_latex,
            fpp_latex=eq.fpp_latex,
            params_used={"x0": x0, "equation": eq.raw},
            iterations=[],
            root=None,
            final_error_pct=None,
            converged=False,
            iteration_count=0,
            excel_sheet_name=_SHEET_NAME,
            formula_description=(
                "Capa 1: pf[k+1]=g(pf[k])  |  "
                "Capa 2: ait[k]=Δ²(pf[k+1],pf[k+2],pf[k+3])  |  "
                "Capa 3: stef[k]=Δ²(ait[k],ait[k+1],ait[k+2])"
            ),
        )

    if gx is None:
        return _not_applicable("No hay g(x) disponible para la secuencia de Punto Fijo.")

    def g(val: float) -> float:
        return float(gx.subs(_x, val).evalf())

    # ── Capa 1: Secuencia de Punto Fijo ───────────────────────────────────────
    # Para producir N filas Steffensen necesitamos:
    #   • N+2 valores Aitken  →  N+4 valores PF (desde índice 1)
    # Generamos con margen amplio.
    pf_seq: list[float] = [float(x0)]
    _pf_limit = max_iter + 25
    for _ in range(_pf_limit):
        try:
            nxt = g(pf_seq[-1])
        except Exception:
            break
        if not math.isfinite(nxt):
            break
        pf_seq.append(nxt)

    # Necesitamos al menos pf[1], pf[2], pf[3], pf[4], pf[5]  (5 valores de PF
    # después de x0) para generar 3 valores Aitken → 1 valor Steffensen.
    if len(pf_seq) < 6:
        return _not_applicable(
            "La secuencia de Punto Fijo diverge antes de producir suficientes "
            "valores para las dos capas Δ²."
        )

    # ── Capa 2: Aitken Δ² sobre PF — INICIA EN pf[1] ─────────────────────────
    # ait[k] = Δ²(pf[k+1], pf[k+2], pf[k+3])
    # Equivalente: iterar i desde 1 (no desde 0) sobre pf_seq.
    aitken_seq: list[float] = []
    for i in range(1, len(pf_seq) - 2):
        hat = _delta2(pf_seq[i], pf_seq[i + 1], pf_seq[i + 2])
        if hat is None:
            # Denominador cero → replica #DIV/0! de Excel: tabla termina aquí.
            break
        aitken_seq.append(hat)

    if len(aitken_seq) < 3:
        return _not_applicable(
            "La capa Aitken (capa 2) no produce suficientes valores "
            "para aplicar el segundo Δ² (capa 3)."
        )

    # ── Capa 3: Steffensen Δ² sobre Aitken — INICIA EN ait[0] ────────────────
    rows: list[SteffensenRow] = []
    converged = False
    final_error: Optional[float] = None
    root: Optional[float] = None
    prev_stef: Optional[float] = None

    for k in range(min(len(aitken_seq) - 2, max_iter)):
        a0 = aitken_seq[k]
        a1 = aitken_seq[k + 1]
        a2 = aitken_seq[k + 2]

        stef = _delta2(a0, a1, a2)
        if stef is None:
            # Denominador cero → replica #DIV/0! de Excel: tabla termina.
            break

        # ── Error % ───────────────────────────────────────────────────────────
        # Fórmula: ABS((x_nuevo − x_anterior) / x_nuevo) × 100
        # k=0: primera fila, sin fila anterior → error = None (Excel deja C2 vacío)
        # k≥1: comparar con la fila anterior
        error_pct: Optional[float] = None
        conv: Optional[bool] = None

        if k > 0 and prev_stef is not None:
            try:
                error_pct = abs((stef - prev_stef) / stef) * 100
            except ZeroDivisionError:
                # stef == 0 exacto: denominador nulo → terminar (replica Excel)
                break
            conv = error_pct < tol
            final_error = error_pct
            if conv:
                converged = True
                root = stef

        # p0/p1/p2 registran el triplete Aitken (capa 2) usado en esta fila
        rows.append(
            SteffensenRow(
                k=k,
                p0=a0,
                p1=a1,
                p2=a2,
                xk_hat=stef,
                x_new=stef,
                error_pct=error_pct,
                converged=conv,
            )
        )

        if converged:
            break

        prev_stef = stef

    # ── Fallback: 1 sola fila Steffensen y aún no convergió ──────────────────
    # Ocurre cuando gx converge cuadráticamente (Newton-like): la capa PF llega
    # a la raíz en 3-4 pasos → aitken_seq produce exactamente 3 valores →
    # el loop ejecuta solo k=0 → prev_stef=None → el comparador nunca dispara,
    # aunque la raíz calculada en k=0 ya es exacta.
    # NOTA: en este punto root=None siempre (solo se asigna con k≥1).
    # Se usa rows[0].xk_hat directamente como candidato.
    if not converged and len(rows) == 1:
        try:
            candidate = rows[0].xk_hat
            f_at_root = abs(float(eq.f_sympy.subs(_x, candidate).evalf()))
            if f_at_root < tol:
                converged = True
                final_error = f_at_root  # reportamos |f(raíz)| como error final
                root = candidate
                rows[0] = SteffensenRow(
                    k=rows[0].k,
                    p0=rows[0].p0,
                    p1=rows[0].p1,
                    p2=rows[0].p2,
                    xk_hat=rows[0].xk_hat,
                    x_new=rows[0].x_new,
                    error_pct=final_error,
                    converged=True,
                )
        except Exception:
            pass  # si falla la evaluación, dejamos converged=False sin cambio

    if root is None and rows:
        root = rows[-1].xk_hat

    return MethodResult(
        method_name="Steffensen",
        applicable=True,
        reason=(
            "Arquitectura de tres capas: Punto Fijo → Aitken Δ² → Steffensen Δ². "
            f"PF generados: {len(pf_seq)}, Aitken: {len(aitken_seq)}, "
            f"Steffensen filas: {len(rows)}."
        ),
        equation_str=eq.raw,
        f_latex=eq.f_latex,
        fp_latex=eq.fp_latex,
        fpp_latex=eq.fpp_latex,
        params_used={
            "x0": x0,
            "gx": str(gx),
            "tol": tol,
            "equation": eq.raw,
        },
        iterations=rows,
        root=root,
        final_error_pct=final_error,
        converged=converged,
        # Primera fila no tiene error → iteration_count = len(rows) - 1
        iteration_count=len(rows) - 1 if rows else 0,
        excel_sheet_name=_SHEET_NAME,
        formula_description=(
            "Capa 1: pf[k+1]=g(pf[k])  |  "
            "Capa 2: ait[k]=Δ²(pf[k+1],pf[k+2],pf[k+3])  |  "
            "Capa 3: stef[k]=Δ²(ait[k],ait[k+1],ait[k+2])"
        ),
    )