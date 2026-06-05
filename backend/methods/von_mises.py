"""
Método de Von Mises.
Matches amburger.xlsx sheet 'Von Mises'.
Formula: xₙ₊₁ = xₙ − f(xₙ) / f'(x₀)
f'(x₀) is computed ONCE at x₀ and held constant throughout all iterations.
"""

from __future__ import annotations
import math
from typing import Optional

from ..core.equation_parser import ParsedEquation, eval_f, eval_fp
from ..core.auto_params import AutoParams
from ..schemas.models import MethodResult, VonMisesRow

_TOLERANCE = 0.00001
_MAX_ITER = 25
_SHEET_NAME = "Von Mises"


def run(
    eq: ParsedEquation,
    params: AutoParams,
    x0: Optional[float] = None,
    max_iter: int = _MAX_ITER,
    tol: float = _TOLERANCE,
) -> MethodResult:
    x0 = x0 if x0 is not None else params.x0_von_mises

    params_used = {"x0": x0, "tol": tol, "max_iter": max_iter, "equation": eq.raw}

    try:
        fp_x0 = eval_fp(eq, x0)
    except Exception as e:
        return MethodResult(
            method_name="Von Mises", applicable=False,
            reason=f"Error en f'(x₀): {e}",
            equation_str=eq.raw, f_latex=eq.f_latex, fp_latex=eq.fp_latex,
            fpp_latex=eq.fpp_latex, params_used=params_used,
            iterations=[], root=None, final_error_pct=None,
            converged=False, iteration_count=0,
            excel_sheet_name=_SHEET_NAME,
            formula_description="xₙ₊₁ = xₙ − f(xₙ) / f'(x₀)",
        )

    if abs(fp_x0) < 1e-12:
        return MethodResult(
            method_name="Von Mises", applicable=False,
            reason=f"f'(x₀) = {fp_x0:.2e} ≈ 0. División por cero.",
            equation_str=eq.raw, f_latex=eq.f_latex, fp_latex=eq.fp_latex,
            fpp_latex=eq.fpp_latex, params_used=params_used,
            iterations=[], root=None, final_error_pct=None,
            converged=False, iteration_count=0,
            excel_sheet_name=_SHEET_NAME,
            formula_description="xₙ₊₁ = xₙ − f(xₙ) / f'(x₀)",
        )

    params_used["fp_x0"] = fp_x0

    rows: list[VonMisesRow] = []
    xk = x0
    converged = False
    final_error: Optional[float] = None
    root: Optional[float] = None

    for k in range(max_iter + 1):
        fxk = eval_f(eq, xk)
        x_next = xk - fxk / fp_x0

        if abs(x_next) > 1e-15:
            error_pct = abs((x_next - xk) / x_next) * 100
        else:
            error_pct = abs(x_next - xk) * 100

        conv = error_pct < tol
        final_error = error_pct

        rows.append(VonMisesRow(
            k=k, xk=xk, fxk=fxk, fp_x0=fp_x0,
            x_next=x_next, x_new=x_next, error_pct=error_pct, converged=conv,
        ))

        if conv:
            converged = True
            root = x_next
            break

        xk = x_next

    if root is None and rows:
        root = rows[-1].x_next

    return MethodResult(
        method_name="Von Mises", applicable=True,
        reason=f"f'(x₀) = {fp_x0:.6f} (constante para todas las iteraciones).",
        equation_str=eq.raw, f_latex=eq.f_latex, fp_latex=eq.fp_latex,
        fpp_latex=eq.fpp_latex, params_used=params_used,
        iterations=rows, root=root, final_error_pct=final_error,
        converged=converged, iteration_count=len(rows) - 1,
        excel_sheet_name=_SHEET_NAME,
        formula_description="xₙ₊₁ = xₙ − f(xₙ) / f'(x₀)",
    )