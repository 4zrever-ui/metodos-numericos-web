"""
Método de Punto Fijo.
Matches amburger.xlsx sheet 'Punto Fijo'.
g(x) is auto-generated or passed explicitly.
"""

from __future__ import annotations
import math
from typing import Optional, Callable

import sympy as sp

from ..core.equation_parser import ParsedEquation, eval_f
from ..core.auto_params import AutoParams
from ..schemas.models import MethodResult, FixedPointRow

_TOLERANCE = 0.00001
_MAX_ITER = 25
_SHEET_NAME = "Punto Fijo"
_x = sp.Symbol("x")


def _check_applicability(
    eq: ParsedEquation, params: AutoParams, x0: float
) -> tuple[bool, str]:
    if params.gx_sympy is None:
        return False, "No se pudo generar una función g(x) con |g'(x)| < 1 para garantizar convergencia."

    try:
        gp = sp.diff(params.gx_sympy, _x)
        gp_val = abs(float(gp.subs(_x, x0).evalf()))
    except Exception:
        gp_val = float("inf")

    if gp_val >= 1:
        return (
            False,
            f"La g(x) generada tiene |g'(x₀)| = {gp_val:.4f} ≥ 1. "
            "No se garantiza convergencia.",
        )

    return True, f"|g'(x₀)| = {gp_val:.6f} < 1. Convergencia garantizada localmente."


def run(
    eq: ParsedEquation,
    params: AutoParams,
    x0: Optional[float] = None,
    gx_sympy: Optional[sp.Expr] = None,
    max_iter: int = _MAX_ITER,
    tol: float = _TOLERANCE,
) -> MethodResult:
    x0 = x0 if x0 is not None else params.x0
    gx = gx_sympy if gx_sympy is not None else params.gx_sympy

    # Build callable g
    if gx is not None:
        def g(val: float) -> float:
            return float(gx.subs(_x, val).evalf())
    else:
        g = None

    applicable, reason = _check_applicability(eq, params, x0)

    # Build gx_excel for reporting
    gx_excel = params.gx_excel
    gx_latex = params.gx_latex

    params_used = {
        "x0": x0,
        "gx": str(gx),
        "gx_latex": gx_latex,
        "tol": tol,
        "max_iter": max_iter,
        "equation": eq.raw,
    }

    if not applicable or g is None:
        return MethodResult(
            method_name="Punto Fijo",
            applicable=False,
            reason=reason,
            equation_str=eq.raw,
            f_latex=eq.f_latex,
            fp_latex=eq.fp_latex,
            fpp_latex=eq.fpp_latex,
            params_used=params_used,
            iterations=[],
            root=None,
            final_error_pct=None,
            converged=False,
            iteration_count=0,
            excel_sheet_name=_SHEET_NAME,
            formula_description="xₙ₊₁ = g(xₙ)",
        )

    rows: list[FixedPointRow] = []
    xk = x0
    converged = False
    final_error: Optional[float] = None
    root: Optional[float] = None

    # k=0: just compute g(x0), no error
    try:
        gxk = g(xk)
    except Exception as e:
        return MethodResult(
            method_name="Punto Fijo",
            applicable=False,
            reason=f"Error evaluando g(x): {str(e)}",
            equation_str=eq.raw,
            f_latex=eq.f_latex,
            fp_latex=eq.fp_latex,
            fpp_latex=eq.fpp_latex,
            params_used=params_used,
            iterations=[],
            root=None,
            final_error_pct=None,
            converged=False,
            iteration_count=0,
            excel_sheet_name=_SHEET_NAME,
            formula_description="xₙ₊₁ = g(xₙ)",
        )

    rows.append(FixedPointRow(k=0, xk=xk, gxk=gxk, x_new=gxk, error_pct=None, converged=None))

    for k in range(1, max_iter + 1):
        prev_xk = xk
        xk = rows[-1].gxk

        try:
            gxk = g(xk)
        except Exception as e:
            return MethodResult(
                method_name="Punto Fijo",
                applicable=False,
                reason=f"Error evaluando g(x) en iteración {k}: {str(e)}",
                equation_str=eq.raw,
                f_latex=eq.f_latex,
                fp_latex=eq.fp_latex,
                fpp_latex=eq.fpp_latex,
                params_used=params_used,
                iterations=rows,
                root=None,
                final_error_pct=None,
                converged=False,
                iteration_count=max(0, len(rows) - 1),
                excel_sheet_name=_SHEET_NAME,
                formula_description="xₙ₊₁ = g(xₙ)",
            )

        if not math.isfinite(gxk):
            break

        if abs(gxk) > 1e-15:
            error_pct = abs((gxk - xk) / gxk) * 100
        else:
            error_pct = abs(gxk - xk) * 100

        conv = error_pct < tol
        final_error = error_pct

        rows.append(FixedPointRow(k=k, xk=xk, gxk=gxk, x_new=gxk, error_pct=error_pct, converged=conv))

        if conv:
            converged = True
            root = gxk
            break

    # Paso 1 (coherencia): si NO convergió, root queda None (no la última iteración).

    return MethodResult(
        method_name="Punto Fijo",
        applicable=True,
        reason=reason,
        equation_str=eq.raw,
        f_latex=eq.f_latex,
        fp_latex=eq.fp_latex,
        fpp_latex=eq.fpp_latex,
        params_used=params_used,
        iterations=rows,
        root=root,
        final_error_pct=final_error,
        converged=converged,
        iteration_count=max(0, len(rows) - 1),
        excel_sheet_name=_SHEET_NAME,
        formula_description="xₙ₊₁ = g(xₙ)",
    )