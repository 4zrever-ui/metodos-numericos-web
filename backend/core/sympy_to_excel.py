"""
sympy_to_excel.py
-----------------
Transpiles SymPy expressions into valid Excel formula strings.

Responsibilities:
- Convert SymPy Expr → Excel string with a given cell reference (e.g. "B3")
- Handle: powers, roots, logarithms, exponentials, trigonometrics, abs
- Produce first and second symbolic derivatives as Excel strings
- All output formulas use cell references, never literal numbers
"""

from __future__ import annotations
import sympy as sp
from sympy import (
    Symbol, Pow, Mul, Add, Rational, Integer, Float, Number,
    log, exp, sqrt, Abs,
    sin, cos, tan, asin, acos, atan,
    sinh, cosh, tanh,
)

x = Symbol("x")


# ---------------------------------------------------------------------------
# Core recursive converter
# ---------------------------------------------------------------------------

def _expr_to_excel(expr: sp.Expr, cell_ref: str) -> str:
    """
    Recursively convert a SymPy expression to an Excel formula fragment.
    cell_ref: e.g. "B3" — replaces every occurrence of the free variable x.
    """
    # --- Symbol -------------------------------------------------------
    if isinstance(expr, Symbol):
        return cell_ref

    # --- Integer / Float / Rational  ----------------------------------
    if isinstance(expr, (Integer, Float, Rational)):
        val = float(expr)
        # Drop unnecessary .0 for clean formulas
        if val == int(val):
            return str(int(val))
        return repr(val)

    if isinstance(expr, Number):
        val = float(expr)
        if val == int(val):
            return str(int(val))
        return repr(val)

    # --- Negation  (Mul with -1) -------------------------------------
    if isinstance(expr, Mul):
        args = expr.args
        # Detect -1 * something
        if args[0] == sp.Integer(-1) and len(args) == 2:
            inner = _expr_to_excel(args[1], cell_ref)
            return f"-{_paren(args[1], inner)}"
        parts = [_expr_to_excel(a, cell_ref) for a in args]
        # Wrap additions/subtractions inside a product
        wrapped = []
        for a, p in zip(args, parts):
            if isinstance(a, Add):
                wrapped.append(f"({p})")
            else:
                wrapped.append(p)
        return "*".join(wrapped)

    # --- Addition  ----------------------------------------------------
    if isinstance(expr, Add):
        parts = []
        for a in expr.args:
            s = _expr_to_excel(a, cell_ref)
            parts.append(s)
        # Join: if a part starts with "-" use as-is, otherwise "+"
        result = parts[0]
        for p in parts[1:]:
            if p.startswith("-"):
                result += p
            else:
                result += "+" + p
        return result

    # --- Power  -------------------------------------------------------
    if isinstance(expr, Pow):
        base, exp_val = expr.args

        # sqrt(x)  ↔  Pow(x, 1/2)
        if exp_val == sp.Rational(1, 2):
            inner = _expr_to_excel(base, cell_ref)
            return f"SQRT({inner})"

        # x^(-1)  ↔  1/x
        if exp_val == sp.Integer(-1):
            inner = _expr_to_excel(base, cell_ref)
            return f"(1/{_paren(base, inner)})"

        # x^(-n)  ↔  1/x^n
        if isinstance(exp_val, (Integer, Rational, Float)) and float(exp_val) < 0:
            pos_exp = -exp_val
            b = _expr_to_excel(base, cell_ref)
            e = _expr_to_excel(pos_exp, cell_ref)
            return f"(1/{_paren(base, b)}^{e})"

        b = _expr_to_excel(base, cell_ref)
        e = _expr_to_excel(exp_val, cell_ref)
        # Wrap base if it's a compound expression
        if isinstance(base, (Add, Mul)):
            b = f"({b})"
        # Wrap exponent only for compound expressions or non-integer rationals
        if isinstance(exp_val, (Add, Mul)):
            e = f"({e})"
        elif isinstance(exp_val, Rational) and not isinstance(exp_val, Integer):
            # e.g. 2/3 → (2/3) but NOT 2 → (2)
            e = f"({e})"
        return f"{b}^{e}"

    # --- Functions  ---------------------------------------------------
    func = type(expr)
    inner_arg = _expr_to_excel(expr.args[0], cell_ref)

    if func == sp.log:
        # SymPy log with two args = log(x, base)
        if len(expr.args) == 2:
            base_arg = _expr_to_excel(expr.args[1], cell_ref)
            return f"LOG({inner_arg},{base_arg})"
        return f"LN({inner_arg})"

    if func == sp.exp:
        return f"EXP({inner_arg})"

    if func == sp.sqrt:
        return f"SQRT({inner_arg})"

    if func == sp.Abs:
        return f"ABS({inner_arg})"

    trig_map = {
        sp.sin: "SIN", sp.cos: "COS", sp.tan: "TAN",
        sp.asin: "ASIN", sp.acos: "ACOS", sp.atan: "ATAN",
        sp.sinh: "SINH", sp.cosh: "COSH", sp.tanh: "TANH",
    }
    if func in trig_map:
        return f"{trig_map[func]}({inner_arg})"

    # Fallback: use SymPy's string with manual x replacement
    raw = str(expr).replace("**", "^").replace("x", cell_ref)
    return raw


def _paren(expr: sp.Expr, rendered: str) -> str:
    """Wrap rendered string in parens if the expression is compound."""
    if isinstance(expr, (Add, Mul)):
        return f"({rendered})"
    return rendered


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def to_excel_formula(sympy_expr: sp.Expr | str, cell_ref: str) -> str:
    """
    Convert a SymPy expression (or string) to an Excel formula string.

    Parameters
    ----------
    sympy_expr : SymPy Expr or parseable string
    cell_ref   : Excel cell reference for the variable x, e.g. "B3"

    Returns
    -------
    str — Excel formula without leading "=", e.g. "B3^3-4*B3+1"
    """
    if isinstance(sympy_expr, str):
        sympy_expr = sp.sympify(sympy_expr, locals={"x": x})
    return _expr_to_excel(sympy_expr, cell_ref)


def get_derivative(sympy_expr: sp.Expr | str, order: int = 1) -> sp.Expr:
    """Return the nth derivative of the expression with respect to x."""
    if isinstance(sympy_expr, str):
        sympy_expr = sp.sympify(sympy_expr, locals={"x": x})
    return sp.diff(sympy_expr, x, order)


def derivative_to_excel(sympy_expr: sp.Expr | str, cell_ref: str, order: int = 1) -> str:
    """
    Return the Excel formula string for the nth derivative evaluated at cell_ref.
    """
    deriv = get_derivative(sympy_expr, order)
    return to_excel_formula(deriv, cell_ref)


def evaluate_derivative_at(sympy_expr: sp.Expr | str, x_val: float, order: int = 1) -> float:
    """
    Numerically evaluate the nth derivative at a given x value.
    Used for constant terms (e.g. f''(x₀) hardcoded).
    """
    if isinstance(sympy_expr, str):
        sympy_expr = sp.sympify(sympy_expr, locals={"x": x})
    deriv = sp.diff(sympy_expr, x, order)
    return float(deriv.subs(x, x_val))


def expr_to_sympy(expr_str: str) -> sp.Expr:
    """Parse a string into a SymPy expression."""
    return sp.sympify(expr_str, locals={"x": x})
