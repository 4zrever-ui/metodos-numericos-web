"""
Método de Steffensen.
Matches amburger.xlsx sheet 'Steffensen'.
Applies Aitken Δ² on the Aitken sequence (acceleration of acceleration).
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


def _delta2(p0: float, p1: float, p2: float) -> float:
    denom = p2 - 2 * p1 + p0
    if abs(denom) < 1e-15:
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
    x0 = x0 if x0 is not None else params.x0
    gx = gx_sympy if gx_sympy is not None else params.gx_sympy

    if gx is None:
        return MethodResult(
            method_name="Steffensen",
            applicable=False,
            reason="No hay g(x) disponible.",
            equation_str=eq.raw,
            f_latex=eq.f_latex, fp_latex=eq.fp_latex, fpp_latex=eq.fpp_latex,
            params_used={"x0": x0, "equation": eq.raw},
            iterations=[], root=None, final_error_pct=None,
            converged=False, iteration_count=0,
            excel_sheet_name=_SHEET_NAME,
            formula_description="p̂ₖ = pₖ − (pₖ₊₁−pₖ)² / (pₖ₊₂ − 2pₖ₊₁ + pₖ)  [sobre secuencia Aitken]",
        )

    def g(val: float) -> float:
        return float(gx.subs(_x, val).evalf())

    # Generate extended Punto Fijo sequence
    base_seq = [x0]
    for _ in range(max_iter + 10):
        try:
            nxt = g(base_seq[-1])
            if not math.isfinite(nxt):
                break
            base_seq.append(nxt)
        except Exception:
            break

    if len(base_seq) < 5:
        return MethodResult(
            method_name="Steffensen",
            applicable=False,
            reason="Secuencia base insuficiente para Steffensen.",
            equation_str=eq.raw,
            f_latex=eq.f_latex, fp_latex=eq.fp_latex, fpp_latex=eq.fpp_latex,
            params_used={"x0": x0, "equation": eq.raw},
            iterations=[], root=None, final_error_pct=None,
            converged=False, iteration_count=0,
            excel_sheet_name=_SHEET_NAME,
            formula_description="p̂ₖ = pₖ − (pₖ₊₁−pₖ)² / (pₖ₊₂ − 2pₖ₊₁ + pₖ)  [sobre secuencia Aitken]",
        )

    # Build Aitken sequence from Punto Fijo base
    aitken_seq = []
    for i in range(len(base_seq) - 2):
        hat = _delta2(base_seq[i], base_seq[i + 1], base_seq[i + 2])
        aitken_seq.append(hat)

    if len(aitken_seq) < 3:
        return MethodResult(
            method_name="Steffensen",
            applicable=False,
            reason="Secuencia Aitken insuficiente para aplicar Steffensen.",
            equation_str=eq.raw,
            f_latex=eq.f_latex, fp_latex=eq.fp_latex, fpp_latex=eq.fpp_latex,
            params_used={"x0": x0, "equation": eq.raw},
            iterations=[], root=None, final_error_pct=None,
            converged=False, iteration_count=0,
            excel_sheet_name=_SHEET_NAME,
            formula_description="p̂ₖ",
        )

    # Apply Δ² on Aitken sequence
    rows: list[SteffensenRow] = []
    converged = False
    final_error: Optional[float] = None
    root: Optional[float] = None
    prev_hat: Optional[float] = None

    for k in range(len(aitken_seq) - 2):
        p0 = aitken_seq[k]
        p1 = aitken_seq[k + 1]
        p2 = aitken_seq[k + 2]

        hat = _delta2(p0, p1, p2)

        error_pct: Optional[float] = None
        conv: Optional[bool] = None

        if k > 0 and prev_hat is not None:
            if abs(hat) > 1e-15:
                error_pct = abs((hat - prev_hat) / hat) * 100
            else:
                error_pct = abs(hat - prev_hat) * 100
            conv = error_pct < tol
            final_error = error_pct
            if conv:
                converged = True
                root = hat

        rows.append(SteffensenRow(k=k, xk_hat=hat, x_new=hat, error_pct=error_pct, converged=conv))

        if converged:
            break
        prev_hat = hat
        if k >= max_iter:
            break

    if root is None and rows:
        root = rows[-1].xk_hat

    return MethodResult(
        method_name="Steffensen",
        applicable=True,
        reason="Δ² aplicado sobre secuencia Aitken.",
        equation_str=eq.raw,
        f_latex=eq.f_latex, fp_latex=eq.fp_latex, fpp_latex=eq.fpp_latex,
        params_used={"x0": x0, "gx": str(gx), "tol": tol, "equation": eq.raw},
        iterations=rows,
        root=root,
        final_error_pct=final_error,
        converged=converged,
        iteration_count=len(rows) - 1,
        excel_sheet_name=_SHEET_NAME,
        formula_description="p̂ₖ = pₖ − (pₖ₊₁−pₖ)² / (pₖ₊₂ − 2pₖ₊₁ + pₖ)  [sobre secuencia Aitken]",
    )