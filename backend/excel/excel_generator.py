"""
excel_generator.py
------------------
Public API for generating Excel workbooks with real formula-based sheets.

Entry points:
  generate_single(method_key, ...)  → bytes (xlsx)
  generate_all(...)                 → bytes (xlsx, 14 sheets)

Both functions return the raw .xlsx bytes, ready to be written to disk
or streamed via FastAPI.

Integration contract with existing backend modules:
  - Expects fx_str as a string parseable by SymPy (e.g. "x**2 - 2")
  - Derivatives are computed internally via sympy_to_excel.py
  - params dict keys must match what excel_templates.py expects
  - Does NOT call biseccion.py / newton_raphson.py etc. — it generates
    Excel files independently using the same mathematical definitions.

Sheet order matches amburger.xlsx:
  1  Bisección           8  Newton 2do Orden
  2  Regula Falsi        9  Chebyshev
  3  Punto Fijo         10  Halley
  4  Aitken             11  Super Halley
  5  Steffensen         12  Ostrowsky
  6  Newton-Raphson     13  Secante
  7  Newton Modificado  14  Von Mises
"""

from __future__ import annotations
import io
from typing import Any

from openpyxl import Workbook

from backend.core.sympy_to_excel import expr_to_sympy, to_excel_formula, derivative_to_excel
from backend.excel.excel_templates import TEMPLATE_REGISTRY


# ---------------------------------------------------------------------------
# Sheet display names (preserves exact naming from amburger.xlsx)
# ---------------------------------------------------------------------------

SHEET_NAMES: dict[str, str] = {
    "biseccion":         "Bisección",
    "regula_falsi":      "Regula Falsi",
    "punto_fijo":        "Punto Fijo",
    "aitken":            "Aitken",
    "steffensen":        "Steffensen",
    "newton_raphson":    "Newton-Raphson",
    "newton_modificado": "Newton Modificado",
    "newton_2do_orden":  "Newton 2do Orden",
    "chebyshev":         "Chebyshev",
    "halley":            "Halley",
    "super_halley":      "Super Halley",
    "ostrowsky":         "Ostrowsky",
    "secante":           "Secante",
    "von_mises":         "Von Mises",
}

# Ordered list for full-workbook export
ALL_METHODS: list[str] = [
    "biseccion", "regula_falsi", "punto_fijo",
    "aitken", "steffensen",
    "newton_raphson", "newton_modificado", "newton_2do_orden",
    "chebyshev", "halley", "super_halley", "ostrowsky",
    "secante", "von_mises",
]


# ---------------------------------------------------------------------------
# Derivative helpers
# ---------------------------------------------------------------------------

def _compute_derivatives(fx_str: str) -> tuple[str, str]:
    """Return (fpx_expr_str, fppx_expr_str) as SymPy-parseable strings."""
    import sympy as sp
    from sympy import Symbol
    xsym = Symbol("x")
    expr = expr_to_sympy(fx_str)
    fp  = sp.diff(expr, xsym, 1)
    fpp = sp.diff(expr, xsym, 2)
    return str(fp), str(fpp)


# ---------------------------------------------------------------------------
# Default parameter resolver
# (integrates with auto_params.py when available)
# ---------------------------------------------------------------------------

def _default_params(method_key: str, fx_str: str) -> dict[str, Any]:
    """
    Generate sensible default parameters using auto_params.
    """
    from backend.core.equation_parser import parse_equation
    from backend.core.auto_params import generate_params

    eq = parse_equation(fx_str)
    p  = generate_params(eq)

    interval_methods  = {"biseccion", "regula_falsi"}
    two_point_methods = {"secante"}
    g_methods         = {"punto_fijo", "aitken", "steffensen"}

    gx_str     = str(p.gx_sympy) if p.gx_sympy is not None else "x"
    gx_display = f"g(x) = {gx_str}"

    if method_key in interval_methods:
        return {"a0": p.a, "b0": p.b}
    if method_key in two_point_methods:
        return {"x0": p.x0, "x1": p.x0_alt}
    if method_key in g_methods:
        return {"x0": p.x0, "g_str": gx_str, "g_display": gx_display}
    return {"x0": p.x0}


# ---------------------------------------------------------------------------
# Core sheet builder
# ---------------------------------------------------------------------------

def _build_sheet(wb: Workbook, method_key: str, fx_str: str,
                 params: dict | None, n_iter: int, eq_label: str) -> None:
    """Add a single method sheet to wb."""
    if params is None:
        params = _default_params(method_key, fx_str)

    fpx_str, fppx_str = _compute_derivatives(fx_str)

    sheet_name = SHEET_NAMES[method_key]
    ws = wb.create_sheet(title=sheet_name)

    template_cls = TEMPLATE_REGISTRY[method_key]
    template = template_cls()

    fp_methods = {"newton_raphson", "von_mises"}
    fpp_methods = {
        "newton_modificado", "newton_2do_orden",
        "chebyshev", "halley", "super_halley", "ostrowsky",
    }

    if method_key in fpp_methods:
        template.build(
            ws=ws, fx_str=fx_str, params=params,
            n_iter=n_iter, eq_label=eq_label,
            fpx_str=fpx_str, fppx_str=fppx_str,
        )
    elif method_key in fp_methods:
        template.build(
            ws=ws, fx_str=fx_str, params=params,
            n_iter=n_iter, eq_label=eq_label,
            fpx_str=fpx_str,
        )
    else:
        template.build(
            ws=ws, fx_str=fx_str, params=params,
            n_iter=n_iter, eq_label=eq_label,
        )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_single(
    method_key: str,
    fx_str: str,
    *,
    params: dict | None = None,
    n_iter: int = 25,
    eq_label: str = "",
) -> bytes:
    """
    Generate a single-sheet xlsx for the given method.

    Parameters
    ----------
    method_key : str
        One of the keys in SHEET_NAMES.
    fx_str : str
        f(x) as SymPy-parseable string, e.g. "x**2 - 2"
    params : dict, optional
        Method-specific initial values. Auto-generated if not provided.
    n_iter : int
        Number of iteration rows (default 25).
    eq_label : str
        Human-readable equation for footer, e.g. "f(x) = x² - 2"

    Returns
    -------
    bytes
        Raw .xlsx content ready for download.
    """
    if method_key not in TEMPLATE_REGISTRY:
        raise ValueError(
            f"Unknown method: '{method_key}'. "
            f"Valid options: {list(TEMPLATE_REGISTRY.keys())}"
        )

    wb = Workbook()
    # Remove default empty sheet
    wb.remove(wb.active)

    _build_sheet(wb, method_key, fx_str, params, n_iter, eq_label or fx_str)

    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


def generate_all(
    fx_str: str,
    *,
    params_per_method: dict[str, dict] | None = None,
    n_iter: int = 25,
    eq_label: str = "",
    methods: list[str] | None = None,
) -> bytes:
    """
    Generate a multi-sheet xlsx with all 14 methods (or a subset).

    Parameters
    ----------
    fx_str : str
        f(x) as SymPy-parseable string.
    params_per_method : dict[method_key → params], optional
        Per-method parameter overrides. Unspecified methods use auto-defaults.
    n_iter : int
        Iteration rows per sheet (default 25).
    eq_label : str
        Human-readable equation for all footers.
    methods : list[str], optional
        Subset of method keys to include. Defaults to ALL_METHODS.

    Returns
    -------
    bytes
        Raw .xlsx content with one sheet per method.
    """
    selected = methods or ALL_METHODS
    params_per_method = params_per_method or {}

    wb = Workbook()
    wb.remove(wb.active)

    for method_key in selected:
        if method_key not in TEMPLATE_REGISTRY:
            continue
        method_params = params_per_method.get(method_key)
        _build_sheet(wb, method_key, fx_str, method_params, n_iter, eq_label or fx_str)

    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


# ---------------------------------------------------------------------------
# Convenience: write directly to file (useful for testing)
# ---------------------------------------------------------------------------

def save_single(path: str, method_key: str, fx_str: str, **kwargs) -> None:
    data = generate_single(method_key, fx_str, **kwargs)
    with open(path, "wb") as f:
        f.write(data)


def save_all(path: str, fx_str: str, **kwargs) -> None:
    data = generate_all(fx_str, **kwargs)
    with open(path, "wb") as f:
        f.write(data)
