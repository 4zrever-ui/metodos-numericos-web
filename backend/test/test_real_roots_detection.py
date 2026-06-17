"""
test_real_roots_detection.py — Fuente única de detección de raíces reales (G2 + G7).

Protege `real_roots_from_sympy` (verificación NUMÉRICA de realidad, robusta al
casus irreducibilis) y sus dos consumidores:
  - G7: excel_generator._has_real_roots (ya NO falso "sin raíces" para x³−4x+1).
  - G2: auto_params.generate_params (ya NO inventa raíz fantasma x≈0 para x²+1).
"""

from __future__ import annotations
import pytest
import sympy as sp

from backend.core.auto_params import real_roots_from_sympy, generate_params
from backend.core.equation_parser import parse_equation
from backend.excel.excel_generator import _has_real_roots

# (ecuación, nº de raíces reales esperadas)
CASOS = [
    ("x**3 - 4*x + 1", 3),   # casus irreducibilis: 3 raíces reales (era el bug G7)
    ("x**3 - 2*x - 5", 1),   # 1 raíz real + 2 complejas
    ("x**2 - 4",       2),   # ±2
    ("x**2 + 1",       0),   # sin raíces reales (debe seguir diciéndolo)
]


def test_real_roots_from_sympy_cuenta_correcta():
    """Fuente única: cuenta bien las raíces reales en los 4 casos."""
    for fx, n in CASOS:
        reals = real_roots_from_sympy(sp.sympify(fx))
        assert reals is not None, fx
        assert len(reals) == n, f"{fx}: esperaba {n}, obtuvo {reals}"


def test_has_real_roots_g7():
    """G7: True si hay ≥1 raíz real; False si 0. (x³−4x+1 antes daba False.)"""
    for fx, n in CASOS:
        assert _has_real_roots(fx) is (n > 0), fx


def test_generate_params_roots_approx_g2():
    """G2: x²+1 sin raíz fantasma; x³−4x+1 con sus 3 raíces reales."""
    # x²+1 → roots_approx vacío (antes: [0] fantasma)
    assert generate_params(parse_equation("x**2 + 1")).roots_approx == []
    # x³−4x+1 → las 3 raíces reales (−2.114908, 0.254102, 1.860806)
    roots = generate_params(parse_equation("x**3 - 4*x + 1")).roots_approx
    assert len(roots) == 3
    for val, exp in zip(sorted(roots), [-2.114908, 0.254102, 1.860806]):
        assert val == pytest.approx(exp, abs=1e-3)
