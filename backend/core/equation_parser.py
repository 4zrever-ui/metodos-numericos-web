"""
Equation parser: user string → SymPy expression + derivatives + Excel formula strings.
"""

from __future__ import annotations
import math
import re
from dataclasses import dataclass, field
from typing import Optional

import sympy as sp
from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application,
    convert_xor,
)

_TRANSFORMS = standard_transformations + (
    implicit_multiplication_application,
    convert_xor,
)

_x = sp.Symbol("x")


@dataclass
class ParsedEquation:
    raw: str
    f_sympy: sp.Expr
    fp_sympy: sp.Expr          # f'(x)
    fpp_sympy: sp.Expr         # f''(x)
    f_excel: str               # Excel formula pattern, placeholder {col}{row}
    fp_excel: str
    fpp_value: Optional[float] # numeric value of f''(x) if constant
    f_latex: str
    fp_latex: str
    fpp_latex: str
    x_symbol: sp.Symbol = field(default_factory=lambda: sp.Symbol("x"))


def _clean_input(raw: str) -> str:
    s = raw.strip()
    # Remove f(x)= or f(x) = prefix
    s = re.sub(r"^f\s*\(\s*x\s*\)\s*=\s*", "", s, flags=re.IGNORECASE)
    # Remove trailing = 0
    s = re.sub(r"\s*=\s*0\s*$", "", s)
    # Replace ^ with ** for sympy (convert_xor handles this but belt+suspenders)
    return s


def _sympy_to_excel(expr: sp.Expr, col: str = "{col}", row: str = "{row}") -> str:
    """
    Convert a SymPy expression to an Excel formula string.
    The variable x is replaced by the cell reference col+row.
    col and row are format placeholders; caller fills them via .format(col=..., row=...).
    """
    x = sp.Symbol("x")
    cell_ref = f"{col}{row}"

    # Use sympy's printer then post-process
    from sympy.printing.str import StrPrinter

    class ExcelPrinter(StrPrinter):
        def _print_Symbol(self, expr):
            if expr.name == "x":
                return cell_ref
            return expr.name

        def _print_Pow(self, expr):
            base = self._print(expr.base)
            exp = self._print(expr.exp)
            # Use ^ for Excel power
            if expr.exp == sp.Rational(1, 2):
                return f"SQRT({base})"
            if expr.exp == sp.Rational(-1, 2):
                return f"(1/SQRT({base}))"
            return f"({base})^({exp})"

        def _print_Mul(self, expr):
            # Standard multiplication
            return super()._print_Mul(expr)

        def _print_Abs(self, expr):
            return f"ABS({self._print(expr.args[0])})"

        def _print_sqrt(self, expr):
            return f"SQRT({self._print(expr.args[0])})"

    printer = ExcelPrinter()
    result = printer.doprint(expr)

    # Fix Python-style ** that may slip through from base class
    result = re.sub(r"\*\*", "^", result)

    # Wrap in = for Excel
    return f"={result}"


def parse_equation(raw: str) -> ParsedEquation:
    cleaned = _clean_input(raw)

    try:
        f_sympy = parse_expr(cleaned, transformations=_TRANSFORMS, local_dict={"x": _x})
    except Exception as exc:
        raise ValueError(f"No se pudo parsear la ecuación '{raw}': {exc}") from exc

    fp_sympy = sp.diff(f_sympy, _x)
    fpp_sympy = sp.diff(fp_sympy, _x)

    f_excel = _sympy_to_excel(f_sympy)
    fp_excel = _sympy_to_excel(fp_sympy)

    # Check if fpp is a constant
    fpp_simplified = sp.simplify(fpp_sympy)
    try:
        fpp_value = float(fpp_simplified)
    except (TypeError, ValueError):
        fpp_value = None

    return ParsedEquation(
        raw=raw,
        f_sympy=f_sympy,
        fp_sympy=fp_sympy,
        fpp_sympy=fpp_sympy,
        f_excel=f_excel,
        fp_excel=fp_excel,
        fpp_value=fpp_value,
        f_latex=sp.latex(f_sympy),
        fp_latex=sp.latex(fp_sympy),
        fpp_latex=sp.latex(fpp_sympy),
    )


def _safe_float(val) -> float:
    """
    Convert a SymPy evaluation result to a Python float, robustly.

    SymPy can return values that are not directly convertible to float:
      - zoo  (ComplexInfinity, e.g. 1/0): raises TypeError
      - complex numbers (e.g. sqrt(-1)):  raises TypeError
      - oo / -oo (symbolic infinity):     float() returns inf/-inf
      - nan (indeterminate):              float() returns nan

    In all non-finite or non-convertible cases, return float("nan") so
    callers can use math.isfinite() as a single uniform guard.
    """
    try:
        result = float(val)
    except (TypeError, ValueError):
        return float("nan")
    if not math.isfinite(result):
        return float("nan")
    return result


def eval_f(eq: ParsedEquation, x_val: float) -> float:
    return _safe_float(eq.f_sympy.subs(_x, x_val).evalf())


def eval_fp(eq: ParsedEquation, x_val: float) -> float:
    return _safe_float(eq.fp_sympy.subs(_x, x_val).evalf())


def eval_fpp(eq: ParsedEquation, x_val: float) -> float:
    return _safe_float(eq.fpp_sympy.subs(_x, x_val).evalf())


def excel_f(eq: ParsedEquation, col: str, row: int) -> str:
    """Return Excel formula for f evaluated at cell col+row."""
    formula = _sympy_to_excel(eq.f_sympy, col=col, row=str(row))
    return formula


def excel_fp(eq: ParsedEquation, col: str, row: int) -> str:
    """Return Excel formula for f' evaluated at cell col+row."""
    return _sympy_to_excel(eq.fp_sympy, col=col, row=str(row))