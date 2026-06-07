"""
Método de la Secante. Matches amburger.xlsx sheet 'Secante'.
Formula: xₙ₊₁ = xₙ − f(xₙ)·(xₙ−xₙ₋₁) / (f(xₙ)−f(xₙ₋₁))

Fórmulas verificadas celda a celda contra amburger.xlsx:

  k=0  C2 = =B2^2-2              (sin IFERROR)
  k=1  C3 = =B3^2-2              (sin IFERROR)
       F3 = =B3-(C3*(B3-D3)/(C3-E3))   (sin IFERROR — si falla, #DIV/0! visible)
       G3 = =IFERROR(ABS((F3-B3)/F3)*100, 0)
       H3 = =IF(IFERROR(G3,0)<0.00001,"SI","NO")

  k≥2  C  = =IFERROR(B^2-2, 0)
       F  = =IFERROR(B-(C*(B-D)/(C-E)), B)
       G  = =IFERROR(ABS((F-B)/F)*100, 0)
       H  = =IF(IFERROR(G,0)<0.00001,"SI","NO")

  Nota sobre conv=True cuando denom≈0 (k≥2):
  F cae a B (fallback), G = IFERROR(0/0, 0) = 0, H evalúa 0 < 0.00001 → "SI".
  Es el comportamiento literal del Excel, no una afirmación matemática.
"""

from __future__ import annotations
import math
from typing import Optional

from ..core.equation_parser import ParsedEquation, eval_f
from ..core.auto_params import AutoParams
from ..schemas.models import MethodResult, SecantRow

_TOLERANCE = 0.00001   # hardcoded en cada celda H del Excel
_MAX_ITER = 25
_SHEET_NAME = "Secante"


def _eval_direct(eq: ParsedEquation, x: float) -> float:
    """
    Replica columna C en k=0 y k=1: =B^2-2  (sin IFERROR).
    Propaga la excepción si falla — igual que un #DIV/0! visible en Excel.
    """
    return eval_f(eq, x)


def _eval_iferror(eq: ParsedEquation, x: float) -> float:
    """
    Replica columna C en k≥2: =IFERROR(B^2-2, 0).
    Devuelve 0.0 si falla, igual que el fallback del Excel.
    """
    try:
        result = eval_f(eq, x)
        return result if math.isfinite(result) else 0.0
    except Exception:
        return 0.0


def _secant_step_k1(
    xk: float, fxk: float,
    xk_prev: float, fxk_prev: float,
) -> tuple[float, float, bool]:
    """
    Replica fila k=1 (fila 3 del Excel). F3 sin IFERROR.
    Si denom=0 → ZeroDivisionError, que el llamador captura como applicable=False.
    G3 = IFERROR(ABS((F3-B3)/F3)*100, 0)
    H3 = IF(IFERROR(G3,0)<0.00001,"SI","NO")
    """
    denom = fxk - fxk_prev
    if abs(denom) < 1e-15:
        raise ZeroDivisionError("f(x1)-f(x0)=0 en k=1. Sin IFERROR en F3.")

    x_next = xk - fxk * (xk - xk_prev) / denom

    # G3 = IFERROR(ABS((F3-B3)/F3)*100, 0)
    # try/except replica el mecanismo IFERROR: Excel intenta dividir por F,
    # si genera error devuelve 0. Mismo camino, no solo mismo resultado.
    try:
        error_pct = abs((x_next - xk) / x_next) * 100
        if not math.isfinite(error_pct):
            error_pct = 0.0
    except ZeroDivisionError:
        error_pct = 0.0

    converged = error_pct < _TOLERANCE
    return x_next, error_pct, converged


def _secant_step_k2plus(
    xk: float, fxk: float,
    xk_prev: float, fxk_prev: float,
) -> tuple[float, float, bool]:
    """
    Replica filas k≥2 (filas 4+ del Excel). F con IFERROR(..., B).
    F  = IFERROR(B-(C*(B-D)/(C-E)), B)   → fallback: xk
    G  = IFERROR(ABS((F-B)/F)*100, 0)    → fallback: 0.0
    H  = IF(IFERROR(G,0)<0.00001,"SI","NO")
    Cuando denom=0 → F=B, G=0, H="SI". Replica exacta del Excel.
    """
    denom = fxk - fxk_prev
    if abs(denom) < 1e-15 or not math.isfinite(denom):
        # F = IFERROR(..., B) → x_next = xk
        # G = IFERROR(..., 0) → error_pct = 0.0
        # H: 0 < 0.00001 → True
        return xk, 0.0, True

    x_next = xk - fxk * (xk - xk_prev) / denom

    if not math.isfinite(x_next):
        # Mismo fallback IFERROR
        return xk, 0.0, True

    # G = IFERROR(ABS((F-B)/F)*100, 0)
    # try/except replica el mecanismo IFERROR: Excel intenta dividir por F,
    # si genera error devuelve 0. Mismo camino, no solo mismo resultado.
    try:
        error_pct = abs((x_next - xk) / x_next) * 100
        if not math.isfinite(error_pct):
            error_pct = 0.0
    except ZeroDivisionError:
        error_pct = 0.0

    converged = error_pct < _TOLERANCE
    return x_next, error_pct, converged


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

    # Evaluación inicial — C2=f(x0), C3=f(x1): sin IFERROR
    try:
        fx0 = _eval_direct(eq, x0)
        fx1 = _eval_direct(eq, x1)
    except Exception as e:
        return MethodResult(
            method_name="Secante", applicable=False,
            reason=f"Error evaluando f(x) en puntos iniciales: {e}",
            equation_str=eq.raw, f_latex=eq.f_latex,
            fp_latex=eq.fp_latex, fpp_latex=eq.fpp_latex,
            params_used=params_used, iterations=[],
            root=None, final_error_pct=None, converged=False,
            iteration_count=0, excel_sheet_name=_SHEET_NAME,
            formula_description="xₙ₊₁ = xₙ − f(xₙ)·(xₙ−xₙ₋₁) / (f(xₙ)−f(xₙ₋₁))",
        )

    rows: list[SecantRow] = []

    # ── k=0  (fila 2) ───────────────────────────────────────────────────────
    # B2=x0, C2=f(x0). D2/E2/F2/G2/H2 vacías.
    rows.append(SecantRow(
        k=0, xk=x0, fxk=fx0,
        xk_prev=None, fxk_prev=None,
        x_next=None, x_new=x0,
        error_pct=None, converged=None,
    ))

    # ── k=1  (fila 3) — F3 sin IFERROR ─────────────────────────────────────
    try:
        x2, err1, conv1 = _secant_step_k1(x1, fx1, x0, fx0)
    except ZeroDivisionError as e:
        return MethodResult(
            method_name="Secante", applicable=False,
            reason=str(e),
            equation_str=eq.raw, f_latex=eq.f_latex,
            fp_latex=eq.fp_latex, fpp_latex=eq.fpp_latex,
            params_used=params_used, iterations=rows,
            root=None, final_error_pct=None, converged=False,
            iteration_count=len(rows) - 1, excel_sheet_name=_SHEET_NAME,
            formula_description="xₙ₊₁ = xₙ − f(xₙ)·(xₙ−xₙ₋₁) / (f(xₙ)−f(xₙ₋₁))",
        )

    rows.append(SecantRow(
        k=1, xk=x1, fxk=fx1,
        xk_prev=x0, fxk_prev=fx0,
        x_next=x2, x_new=x2,
        error_pct=err1, converged=conv1,
    ))

    if conv1:
        return MethodResult(
            method_name="Secante", applicable=True,
            reason=f"x₀={x0}, x₁={x1}.",
            equation_str=eq.raw, f_latex=eq.f_latex,
            fp_latex=eq.fp_latex, fpp_latex=eq.fpp_latex,
            params_used=params_used, iterations=rows,
            root=x2, final_error_pct=err1, converged=True,
            iteration_count=len(rows) - 1, excel_sheet_name=_SHEET_NAME,
            formula_description="xₙ₊₁ = xₙ − f(xₙ)·(xₙ−xₙ₋₁) / (f(xₙ)−f(xₙ₋₁))",
        )

    # ── k=2..max_iter  (filas 4+) — C y F con IFERROR ───────────────────────
    converged = False
    final_error: Optional[float] = err1
    root: Optional[float] = None

    xk_prev, fxk_prev = x1, fx1
    xk = x2

    for k in range(2, max_iter + 1):
        fxk = _eval_iferror(eq, xk)          # C = IFERROR(B^2-2, 0)
        x_next, error_pct, conv = _secant_step_k2plus(xk, fxk, xk_prev, fxk_prev)
        final_error = error_pct

        rows.append(SecantRow(
            k=k, xk=xk, fxk=fxk,
            xk_prev=xk_prev, fxk_prev=fxk_prev,
            x_next=x_next, x_new=x_next,
            error_pct=error_pct, converged=conv,
        ))

        if conv:
            converged = True
            root = x_next
            break

        xk_prev, fxk_prev = xk, fxk
        xk = x_next

    if root is None and rows:
        last = rows[-1]
        root = last.x_next if last.x_next is not None else last.xk

    return MethodResult(
        method_name="Secante", applicable=True,
        reason=f"x₀={x0}, x₁={x1}.",
        equation_str=eq.raw, f_latex=eq.f_latex,
        fp_latex=eq.fp_latex, fpp_latex=eq.fpp_latex,
        params_used=params_used, iterations=rows,
        root=root, final_error_pct=final_error,
        converged=converged, iteration_count=len(rows) - 1,
        excel_sheet_name=_SHEET_NAME,
        formula_description="xₙ₊₁ = xₙ − f(xₙ)·(xₙ−xₙ₋₁) / (f(xₙ)−f(xₙ₋₁))",
    )