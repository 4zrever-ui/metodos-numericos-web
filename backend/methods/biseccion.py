"""
Método de Bisección.
Exact logic matching amburger.xlsx sheet 'Bisección'.
Tolerance: error% < 0.00001 (relative %)
"""

from __future__ import annotations
import math
from typing import Optional

from ..core.equation_parser import ParsedEquation, eval_f
from ..core.auto_params import AutoParams
from ..schemas.models import MethodResult, IntervalRow


_TOLERANCE = 0.00001
_MAX_ITER = 25
_SHEET_NAME = "Bisección"


def _check_applicability(eq: ParsedEquation, a: float, b: float) -> tuple[bool, str]:
    try:
        fa = eval_f(eq, a)
        fb = eval_f(eq, b)
    except Exception as e:
        return False, f"Error evaluando f(x): {e}"

    if not math.isfinite(fa) or not math.isfinite(fb):
        return False, "f(x) no es finita en el intervalo."

    if fa * fb > 0:
        return False, (
            f"No existe cambio de signo en [{a}, {b}]: "
            f"f({a})={fa:.6f}, f({b})={fb:.6f}. "
            "Teorema de Bolzano no aplicable."
        )

    return True, f"Cambio de signo detectado en [{a}, {b}]: f({a})={fa:.6f}, f({b})={fb:.6f}."


def run(
    eq: ParsedEquation,
    params: AutoParams,
    a: Optional[float] = None,
    b: Optional[float] = None,
    max_iter: int = _MAX_ITER,
    tol: float = _TOLERANCE,
) -> MethodResult:
    a = a if a is not None else params.a
    b = b if b is not None else params.b

    applicable, reason = _check_applicability(eq, a, b)

    params_used = {
        "a": a,
        "b": b,
        "tol": tol,
        "max_iter": max_iter,
        "equation": eq.raw,
    }

    if not applicable:
        return MethodResult(
            method_name="Bisección",
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
            formula_description="cₙ = (aₙ + bₙ) / 2",
        )

    rows: list[IntervalRow] = []
    cur_a = a
    cur_b = b
    prev_c: Optional[float] = None
    root: Optional[float] = None
    converged = False
    final_error: Optional[float] = None

    for k in range(max_iter + 1):
        fa = eval_f(eq, cur_a)
        c = (cur_a + cur_b) / 2
        fc = eval_f(eq, c)
        fb = eval_f(eq, cur_b)
        fa_fc = fa * fc

        error_pct: Optional[float] = None
        conv: Optional[bool] = None

        if k > 0 and prev_c is not None:
            if abs(c) > 1e-15:
                error_pct = abs((c - prev_c) / c) * 100
            else:
                error_pct = abs(c - prev_c) * 100
            conv = error_pct < tol
            final_error = error_pct
            if conv:
                converged = True
                root = c

        rows.append(
            IntervalRow(
                k=k,
                a=cur_a,
                c=c,
                b=cur_b,
                fa=fa,
                fc=fc,
                fb=fb,
                fa_fc=fa_fc,
                x_new=c,
                error_pct=error_pct,
                converged=conv,
            )
        )

        if converged:
            break

        prev_c = c

        # Update interval
        if fa * fc < 0:
            cur_b = c
        else:
            cur_a = c

    if root is None:
        root = rows[-1].c

    return MethodResult(
        method_name="Bisección",
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
        iteration_count=len(rows) - 1,
        excel_sheet_name=_SHEET_NAME,
        formula_description="cₙ = (aₙ + bₙ) / 2",
    )