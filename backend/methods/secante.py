"""
Método de la Secante.
Matches amburger.xlsx sheet 'Secante'.
Formula: xₙ₊₁ = xₙ − f(xₙ)·(xₙ−xₙ₋₁) / (f(xₙ)−f(xₙ₋₁))
Uses IFERROR protection as in the original Excel.
"""

from __future__ import annotations
import math
from typing import Optional

from ..core.equation_parser import ParsedEquation, eval_f
from ..core.auto_params import AutoParams
from ..schemas.models import MethodResult, SecantRow

_TOLERANCE = 0.00001
_MAX_ITER = 25
_SHEET_NAME = "Secante"


def run(
    eq: ParsedEquation,
    params: AutoParams,
    x0: Optional[float] = None,
    x1: Optional[float] = None,
    max_iter: int = _MAX_ITER,
    tol: float = _TOLERANCE,
) -> MethodResult:
    x0 = x0 if x0 is not None else params.x0
    x1 = x1 if x1 is not None else params.x0_alt

    params_used = {
        "x0": x0, "x1": x1, "tol": tol,
        "max_iter": max_iter, "equation": eq.raw,
    }

    try:
        fx0 = eval_f(eq, x0)
        fx1 = eval_f(eq, x1)
    except Exception as e:
        return MethodResult(
            method_name="Secante", applicable=False,
            reason=f"Error evaluando f(x): {e}",
            equation_str=eq.raw, f_latex=eq.f_latex, fp_latex=eq.fp_latex,
            fpp_latex=eq.fpp_latex, params_used=params_used,
            iterations=[], root=None, final_error_pct=None,
            converged=False, iteration_count=0,
            excel_sheet_name=_SHEET_NAME,
            formula_description="xₙ₊₁ = xₙ − f(xₙ)·(xₙ−xₙ₋₁) / (f(xₙ)−f(xₙ₋₁))",
        )

    rows: list[SecantRow] = []

    # k=0: only x0 and f(x0)
    rows.append(SecantRow(
        k=0, xk=x0, fxk=fx0, xk_prev=None, fxk_prev=None,
        x_next=None, x_new=x0, error_pct=None, converged=None,
    ))

    # k=1: x1, f(x1), x0 as prev, first x_next
    denom = fx1 - fx0
    if abs(denom) < 1e-15:
        x2 = x1
        err1 = 0.0
    else:
        x2 = x1 - fx1 * (x1 - x0) / denom
        if abs(x2) > 1e-15:
            err1 = abs((x2 - x1) / x2) * 100
        else:
            err1 = abs(x2 - x1) * 100

    conv1 = err1 < tol
    rows.append(SecantRow(
        k=1, xk=x1, fxk=fx1, xk_prev=x0, fxk_prev=fx0,
        x_next=x2, x_new=x2, error_pct=err1, converged=conv1,
    ))

    if conv1:
        root = x2
        return MethodResult(
            method_name="Secante", applicable=True,
            reason=f"x₀={x0}, x₁={x1}.",
            equation_str=eq.raw, f_latex=eq.f_latex, fp_latex=eq.fp_latex,
            fpp_latex=eq.fpp_latex, params_used=params_used,
            iterations=rows, root=root, final_error_pct=err1,
            converged=True, iteration_count=1,
            excel_sheet_name=_SHEET_NAME,
            formula_description="xₙ₊₁ = xₙ − f(xₙ)·(xₙ−xₙ₋₁) / (f(xₙ)−f(xₙ₋₁))",
        )

    converged = False
    final_error: Optional[float] = err1
    root: Optional[float] = None
    xk_prev, fxk_prev = x1, fx1
    xk = x2

    for k in range(2, max_iter + 1):
        try:
            fxk = eval_f(eq, xk)
        except Exception:
            fxk = 0.0

        denom = fxk - fxk_prev
        if abs(denom) < 1e-15:
            x_next = xk
            error_pct = 0.0
        else:
            x_next = xk - fxk * (xk - xk_prev) / denom
            if not math.isfinite(x_next):
                x_next = xk
                error_pct = 0.0
            elif abs(x_next) > 1e-15:
                error_pct = abs((x_next - xk) / x_next) * 100
            else:
                error_pct = abs(x_next - xk) * 100

        conv = error_pct < tol
        final_error = error_pct

        rows.append(SecantRow(
            k=k, xk=xk, fxk=fxk, xk_prev=xk_prev, fxk_prev=fxk_prev,
            x_next=x_next, x_new=x_next, error_pct=error_pct, converged=conv,
        ))

        if conv:
            converged = True
            root = x_next
            break

        xk_prev, fxk_prev = xk, fxk
        xk = x_next

    if root is None and rows:
        root = rows[-1].x_next or rows[-1].xk

    return MethodResult(
        method_name="Secante", applicable=True,
        reason=f"x₀={x0}, x₁={x1}.",
        equation_str=eq.raw, f_latex=eq.f_latex, fp_latex=eq.fp_latex,
        fpp_latex=eq.fpp_latex, params_used=params_used,
        iterations=rows, root=root, final_error_pct=final_error,
        converged=converged, iteration_count=len(rows) - 1,
        excel_sheet_name=_SHEET_NAME,
        formula_description="xₙ₊₁ = xₙ − f(xₙ)·(xₙ−xₙ₋₁) / (f(xₙ)−f(xₙ₋₁))",
    )