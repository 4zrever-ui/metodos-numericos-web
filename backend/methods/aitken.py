"""
Método de Aitken (Δ²).
Matches amburger.xlsx sheet 'Aitken'.
Uses Punto Fijo as base iteration.
Formula: p̂ₖ = pₖ₊₁ - (pₖ₊₂ - pₖ₊₁)² / (pₖ₊₃ - 2·pₖ₊₂ + pₖ₊₁)

Architecture confirmed from amburger.xlsx:
  - Base sequence: pf[0]=x0, pf[1]=g(x0), pf[2]=g(pf[1]), ...
  - Aitken rows start using pf[1] (NOT pf[0]) as first triplet anchor.
    Row k uses triplet (pf[k+1], pf[k+2], pf[k+3]).
  - Error is computed starting at row k=1: abs((hat[k]-hat[k-1])/hat[k])*100
  - Convergence check (SI/NO) starts at k=1.
  - First SI stops the method.
  - iteration_count = k (the converged row index).
  - Tolerance = 0.00001.
"""

from __future__ import annotations
import math
from typing import Optional

import sympy as sp

from ..core.equation_parser import ParsedEquation
from ..core.auto_params import AutoParams
from ..schemas.models import MethodResult, AitkenRow

_TOLERANCE = 0.00001
_MAX_ITER = 25
_SHEET_NAME = "Aitken"
_x = sp.Symbol("x")


def _aitken_delta2(p0: float, p1: float, p2: float) -> Optional[float]:
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
            method_name="Aitken (Δ²)",
            applicable=False,
            reason="No hay g(x) disponible para la iteración base de Punto Fijo.",
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
            formula_description="p̂ₖ = pₖ₊₁ − (pₖ₊₂−pₖ₊₁)² / (pₖ₊₃ − 2pₖ₊₂ + pₖ₊₁)",
        )

    def g(val: float) -> float:
        return float(gx.subs(_x, val).evalf())

    # Generate base Punto Fijo sequence.
    # We need pf[0..N] where pf[0] = x0.
    # Aitken row k uses triplet (pf[k+1], pf[k+2], pf[k+3]),
    # so we need at least max_iter+3+1 values.
    base_seq = [x0]
    for _ in range(max_iter + 6):
        try:
            nxt = g(base_seq[-1])
            if not math.isfinite(nxt):
                break
            base_seq.append(nxt)
        except Exception:
            break

    # Need at least 4 values: pf[0], pf[1], pf[2], pf[3]
    # to compute even the first Aitken hat (k=0 using pf[1..3])
    if len(base_seq) < 4:
        return MethodResult(
            method_name="Aitken (Δ²)",
            applicable=False,
            reason="La secuencia base de Punto Fijo diverge. Aitken no aplicable.",
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
            formula_description="p̂ₖ = pₖ₊₁ − (pₖ₊₂−pₖ₊₁)² / (pₖ₊₃ − 2pₖ₊₂ + pₖ₊₁)",
        )

    rows: list[AitkenRow] = []
    converged = False
    final_error: Optional[float] = None
    root: Optional[float] = None
    prev_hat: Optional[float] = None
    converged_k: int = 0

    # Excel architecture: row k uses triplet (pf[k+1], pf[k+2], pf[k+3])
    # Maximum k is limited by available base_seq length
    max_k = min(len(base_seq) - 3, max_iter)

    for k in range(max_k):
        p0 = base_seq[k + 1]
        p1 = base_seq[k + 2]
        p2 = base_seq[k + 3]

        hat = _aitken_delta2(p0, p1, p2)

        if hat is None:
            # denom = 0 → Excel shows #DIV/0!, table ends here.
            break

        error_pct: Optional[float] = None
        conv: Optional[bool] = None

        # Error and convergence start at k=1 (matching Excel column C starting at row 3)
        if k >= 1 and prev_hat is not None:
            if abs(hat) > 1e-15:
                error_pct = abs((hat - prev_hat) / hat) * 100
            else:
                error_pct = abs(hat - prev_hat) * 100
            conv = error_pct < tol
            final_error = error_pct
            if conv:
                converged = True
                root = hat
                converged_k = k

        rows.append(AitkenRow(
            k=k, p0=p0, p1=p1, p2=p2,
            xk_hat=hat, x_new=hat,
            error_pct=error_pct, converged=conv,
        ))

        if converged:
            break

        prev_hat = hat

    if root is None and rows:
        root = rows[-1].xk_hat
        converged_k = rows[-1].k

    return MethodResult(
        method_name="Aitken (Δ²)",
        applicable=True,
        reason=f"Aceleración de Punto Fijo con g(x). |base_seq| = {len(base_seq)}.",
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
        # iteration_count = the k index of the converged (or last) row
        iteration_count=converged_k,
        excel_sheet_name=_SHEET_NAME,
        formula_description="p̂ₖ = pₖ₊₁ − (pₖ₊₂−pₖ₊₁)² / (pₖ₊₃ − 2pₖ₊₂ + pₖ₊₁)",
    )