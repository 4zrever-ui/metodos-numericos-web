"""
Método de Newton-Raphson.
Matches amburger.xlsx sheet 'Newton-Raphson'.
Formula: xₙ₊₁ = xₙ − f(xₙ) / f'(xₙ)
"""

from __future__ import annotations
import math
from typing import Optional

from ..core.equation_parser import ParsedEquation, eval_f, eval_fp
from ..core.auto_params import AutoParams
from ..schemas.models import MethodResult, NewtonRaphsonRow

_TOLERANCE = 0.00001
_MAX_ITER = 25
_SHEET_NAME = "Newton-Raphson"


def _check_applicability(eq: ParsedEquation, x0: float) -> tuple[bool, str]:
    try:
        fp0 = eval_fp(eq, x0)
    except Exception as e:
        return False, f"Error evaluando f'(x₀): {e}"
    if abs(fp0) < 1e-12:
        return False, f"f'(x₀) = {fp0:.2e} ≈ 0. División por cero. Elige otro x₀."
    return True, f"f'(x₀) = {fp0:.6f} ≠ 0. Método aplicable."


def run(
    eq: ParsedEquation,
    params: AutoParams,
    x0: Optional[float] = None,
    max_iter: int = _MAX_ITER,
    tol: float = _TOLERANCE,
) -> MethodResult:
    x0 = x0 if x0 is not None else params.x0
    applicable, reason = _check_applicability(eq, x0)

    params_used = {"x0": x0, "tol": tol, "max_iter": max_iter, "equation": eq.raw}

    if not applicable:
        return MethodResult(
            method_name="Newton-Raphson",
            applicable=False,
            reason=reason,
            equation_str=eq.raw,
            f_latex=eq.f_latex, fp_latex=eq.fp_latex, fpp_latex=eq.fpp_latex,
            params_used=params_used,
            iterations=[], root=x0, final_error_pct=None,
            converged=False, iteration_count=0,
            excel_sheet_name=_SHEET_NAME,
            formula_description="xₙ₊₁ = xₙ − f(xₙ) / f'(xₙ)",
        )

    rows: list[NewtonRaphsonRow] = []
    xk = x0
    converged = False
    final_error: Optional[float] = None
    root: Optional[float] = None

    for k in range(max_iter):
        fxk = eval_f(eq, xk)
        fpxk = eval_fp(eq, xk)

        if abs(fpxk) < 1e-15:
            break

        x_next = xk - fxk / fpxk

        if abs(x_next) > 1e-15:
            error_pct = abs((x_next - xk) / x_next) * 100
        else:
            error_pct = abs(x_next - xk) * 100

        conv = error_pct < tol
        final_error = error_pct

        rows.append(NewtonRaphsonRow(
            k=k, xk=xk, fxk=fxk, fpxk=fpxk, x_next=x_next,
            x_new=x_next, error_pct=error_pct, converged=conv,
        ))

        if conv:
            converged = True
            root = x_next
            break

        xk = x_next

    if root is None and rows:
        root = rows[-1].x_next

    return MethodResult(
        method_name="Newton-Raphson",
        applicable=True,
        reason=reason,
        equation_str=eq.raw,
        f_latex=eq.f_latex, fp_latex=eq.fp_latex, fpp_latex=eq.fpp_latex,
        params_used=params_used,
        iterations=rows,
        root=root,
        final_error_pct=final_error,
        converged=converged,
        iteration_count=len(rows) - 1,
        excel_sheet_name=_SHEET_NAME,
        formula_description="xₙ₊₁ = xₙ − f(xₙ) / f'(xₙ)",
    )