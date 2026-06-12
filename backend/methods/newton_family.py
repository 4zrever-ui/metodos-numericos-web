"""
Higher-order Newton-family methods.
Matches amburger.xlsx sheets:
  - Newton Modificado
  - Newton 2do Orden
  - Chebyshev
  - Halley
  - Super Halley
  - Ostrowsky
"""

from __future__ import annotations
import math
from typing import Optional

from ..core.equation_parser import ParsedEquation, eval_f, eval_fp, eval_fpp
from ..core.auto_params import AutoParams
from ..schemas.models import MethodResult, NewtonModRow

_TOLERANCE = 0.00001
_MAX_ITER = 25


def _base_check(eq: ParsedEquation, x0: float) -> tuple[bool, str]:
    try:
        fp0 = eval_fp(eq, x0)
    except Exception as e:
        return False, f"Error en f'(x₀): {e}"
    if abs(fp0) < 1e-12:
        return False, f"f'(x₀) = {fp0:.2e} ≈ 0."
    return True, f"f'(x₀) = {fp0:.6f} ≠ 0."


def _iterate(
    method_name: str,
    sheet_name: str,
    formula_desc: str,
    step_fn,        # (fxk, fpxk, fppxk, xk) -> x_next
    eq: ParsedEquation,
    params: AutoParams,
    x0: Optional[float],
    max_iter: int,
    tol: float,
    needs_fpp: bool = True,
) -> MethodResult:
    x0 = x0 if x0 is not None else params.x0
    applicable, reason = _base_check(eq, x0)

    params_used = {"x0": x0, "tol": tol, "max_iter": max_iter, "equation": eq.raw}

    if not applicable:
        return MethodResult(
            method_name=method_name, applicable=False, reason=reason,
            equation_str=eq.raw, f_latex=eq.f_latex, fp_latex=eq.fp_latex,
            fpp_latex=eq.fpp_latex, params_used=params_used,
            iterations=[], root=None, final_error_pct=None,
            converged=False, iteration_count=0,
            excel_sheet_name=sheet_name, formula_description=formula_desc,
        )

    rows: list[NewtonModRow] = []
    xk = x0
    converged = False
    final_error: Optional[float] = None
    root: Optional[float] = None

    for k in range(max_iter + 1):
        fxk = eval_f(eq, xk)
        fpxk = eval_fp(eq, xk)
        fppxk = eval_fpp(eq, xk) if needs_fpp else 0.0

        try:
            x_next = step_fn(fxk, fpxk, fppxk, xk)
        except (ZeroDivisionError, ValueError, OverflowError):
            break

        if not math.isfinite(x_next):
            break

        if abs(x_next) > 1e-15:
            error_pct = abs((x_next - xk) / x_next) * 100
        else:
            error_pct = abs(x_next - xk) * 100

        conv = error_pct < tol
        final_error = error_pct

        rows.append(NewtonModRow(
            k=k, xk=xk, fxk=fxk, fpxk=fpxk, fppxk=fppxk,
            x_next=x_next, x_new=x_next, error_pct=error_pct, converged=conv,
        ))

        if conv:
            converged = True
            root = x_next
            break

        xk = x_next

    if root is None:
        root = rows[-1].x_next if rows else xk

    return MethodResult(
        method_name=method_name, applicable=True, reason=reason,
        equation_str=eq.raw, f_latex=eq.f_latex, fp_latex=eq.fp_latex,
        fpp_latex=eq.fpp_latex, params_used=params_used,
        iterations=rows, root=root, final_error_pct=final_error,
        converged=converged, iteration_count=len(rows) - 1,
        excel_sheet_name=sheet_name, formula_description=formula_desc,
    )


# ── Newton Modificado ─────────────────────────────────────────────────────────

def run_newton_modificado(
    eq: ParsedEquation, params: AutoParams,
    x0: Optional[float] = None, max_iter: int = _MAX_ITER, tol: float = _TOLERANCE,
) -> MethodResult:
    def step(f, fp, fpp, x):
        denom = fp ** 2 - f * fpp
        if abs(denom) < 1e-15:
            raise ZeroDivisionError
        return x - (f * fp) / denom

    return _iterate(
        "Newton Modificado", "Newton Modificado",
        "xₙ₊₁ = xₙ − [f·f'] / [(f')²−f·f'']",
        step, eq, params, x0, max_iter, tol,
    )


# ── Newton 2do Orden ──────────────────────────────────────────────────────────

def run_newton_segundo_orden(
    eq: ParsedEquation, params: AutoParams,
    x0: Optional[float] = None, max_iter: int = _MAX_ITER, tol: float = _TOLERANCE,
) -> MethodResult:
    def step(f, fp, fpp, x):
        if abs(fpp) < 1e-15:
            raise ZeroDivisionError
        discriminant = fp ** 2 - 2 * fpp * f
        if discriminant < 0:
            raise ValueError("Discriminante negativo")
        return x + (-fp + math.sqrt(discriminant)) / fpp

    return _iterate(
        "Newton 2do Orden", "Newton 2do Orden",
        "xₙ₊₁ = xₙ + (−f' + √((f')²−2f''·f)) / f''",
        step, eq, params, x0, max_iter, tol,
    )


# ── Chebyshev ─────────────────────────────────────────────────────────────────

def run_chebyshev(
    eq: ParsedEquation, params: AutoParams,
    x0: Optional[float] = None, max_iter: int = _MAX_ITER, tol: float = _TOLERANCE,
) -> MethodResult:
    def step(f, fp, fpp, x):
        if abs(fp) < 1e-15:
            raise ZeroDivisionError
        return x - (f / fp) - (f ** 2 * fpp) / (2 * fp ** 3)

    return _iterate(
        "Chebyshev", "Chebyshev",
        "xₙ₊₁ = xₙ − (f/f') − [(f²·f'') / (2·(f')³)]",
        step, eq, params, x0, max_iter, tol,
    )


# ── Halley ────────────────────────────────────────────────────────────────────

def run_halley(
    eq: ParsedEquation, params: AutoParams,
    x0: Optional[float] = None, max_iter: int = _MAX_ITER, tol: float = _TOLERANCE,
) -> MethodResult:
    def step(f, fp, fpp, x):
        denom = fp - (fpp * f) / (2 * fp)
        if abs(denom) < 1e-15:
            raise ZeroDivisionError
        return x - f / denom

    return _iterate(
        "Halley", "Halley",
        "xₙ₊₁ = xₙ − f / [f' − (f''·f)/(2·f')]",
        step, eq, params, x0, max_iter, tol,
    )


# ── Super Halley ──────────────────────────────────────────────────────────────

def run_super_halley(
    eq: ParsedEquation, params: AutoParams,
    x0: Optional[float] = None, max_iter: int = _MAX_ITER, tol: float = _TOLERANCE,
) -> MethodResult:
    def step(f, fp, fpp, x):
        num = 2 * fp ** 2 - f * fpp
        den = 2 * (fp ** 2 - f * fpp)
        if abs(den) < 1e-15 or abs(fp) < 1e-15:
            raise ZeroDivisionError
        return x - (num / den) * (f / fp)

    return _iterate(
        "Super Halley", "Super Halley",
        "xₙ₊₁ = xₙ − [2(f')²−ff''] / [2((f')²−ff'')] · (f/f')",
        step, eq, params, x0, max_iter, tol,
    )


# ── Ostrowsky ─────────────────────────────────────────────────────────────────

def run_ostrowsky(
    eq: ParsedEquation, params: AutoParams,
    x0: Optional[float] = None, max_iter: int = _MAX_ITER, tol: float = _TOLERANCE,
) -> MethodResult:
    def step(f, fp, fpp, x):
        inner = fp ** 2 - f * fpp
        if inner < 0:
            raise ValueError("Raíz de número negativo en Ostrowsky")
        sqrt_inner = math.sqrt(inner)
        if abs(sqrt_inner) < 1e-15 or abs(fp) < 1e-15:
            raise ZeroDivisionError
        # P1 fix: la forma original (fp/√)·(f/fp) cancelaba fp y perdía su
        # signo (√ siempre ≥ 0) → divergía cuando f'<0. Preservamos el signo
        # de f' con copysign: xₙ₊₁ = xₙ − f·signo(f') / √(f'²−f·f'').
        return x - f * math.copysign(1.0, fp) / sqrt_inner

    return _iterate(
        "Ostrowsky", "Ostrowsky",
        "xₙ₊₁ = xₙ − f·signo(f') / √(f'²−f·f'')",
        step, eq, params, x0, max_iter, tol,
    )