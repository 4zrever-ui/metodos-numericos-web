import math

import pytest
import sympy as sp

from backend.core.auto_params import AutoParams
from backend.core.equation_parser import parse_equation
from backend.methods.punto_fijo import run


_x = sp.Symbol("x")


def _params(gx, x0):
    return AutoParams(
        a=0.0,
        b=3.0,
        x0=x0,
        x0_alt=2.0,
        x0_von_mises=x0,
        tol=1e-10,
        max_iter=25,
        gx_sympy=gx,
        gx_excel="",
        gx_latex="",
        gx_candidates=[],
        roots_approx=[],
        f_sign_change_found=False,
    )


def test_racional_iteraciones_y_raiz_sqrt2(eq_cuadratica):
    gx = (_x + 2) / (_x + 1)
    result = run(eq_cuadratica, _params(gx, 1.0), x0=1.0, tol=1e-10)

    assert result.applicable is True
    assert result.converged is True
    assert [row.x_new for row in result.iterations[:4]] == pytest.approx(
        [1.5, 1.4, 17 / 12, 41 / 29], rel=0.0, abs=1e-12
    )
    assert result.root == pytest.approx(math.sqrt(2), rel=0.0, abs=1e-12)


def test_cubica_cbrt_converge_a_raiz_esperada():
    eq = parse_equation("x**3 - 2*x - 5")
    gx = sp.cbrt(2 * _x + 5)
    result = run(eq, _params(gx, 2.0), x0=2.0, tol=1e-10)

    assert result.applicable is True
    assert result.converged is True
    assert result.root == pytest.approx(2.0945514815, rel=0.0, abs=1e-10)


def test_cubica_gx_repulsora_inaplicable_sin_iteraciones():
    eq = parse_equation("x**3 - 2*x - 5")
    gx = (_x**3 - 5) / 2
    result = run(eq, _params(gx, 2.0), x0=2.0)

    assert result.applicable is False
    assert "6.0000" in result.reason
    assert result.iterations == []
    assert result.iteration_count == 0
    assert result.converged is False
    assert result.root is None


def test_gx_none_inaplicable(eq_cuadratica, params_gx_none):
    result = run(eq_cuadratica, params_gx_none)

    assert result.applicable is False
    assert result.iterations == []
    assert result.iteration_count == 0
    assert result.converged is False
    assert result.root is None


def test_tolerancia_laxa_detiene_en_k3_y_devuelve_x_new(eq_cuadratica):
    gx = (_x + 2) / (_x + 1)
    result = run(eq_cuadratica, _params(gx, 1.0), x0=1.0, tol=1.0)

    assert result.converged is True
    assert result.iteration_count == 3
    assert result.root == pytest.approx(41 / 29, rel=0.0, abs=1e-12)
    assert result.root != pytest.approx(17 / 12, rel=0.0, abs=1e-12)
    last = result.iterations[-1]
    assert last.k == 3
    assert last.xk == pytest.approx(17 / 12, rel=0.0, abs=1e-12)
    assert last.x_new == pytest.approx(41 / 29, rel=0.0, abs=1e-12)


def test_error_porcentual_por_fila(eq_cuadratica):
    gx = (_x + 2) / (_x + 1)
    result = run(eq_cuadratica, _params(gx, 1.0), x0=1.0, tol=1e-10)
    rows = {row.k: row for row in result.iterations}

    assert rows[0].error_pct is None
    assert rows[1].error_pct == pytest.approx(50 / 7, rel=0.0, abs=1e-9)
    assert rows[2].error_pct == pytest.approx(20 / 17, rel=0.0, abs=1e-9)
    assert rows[3].error_pct == pytest.approx(25 / 123, rel=0.0, abs=1e-9)


def test_max_iter_sin_convergencia_no_devuelve_raiz(eq_cuadratica):
    gx = (_x + 2) / (_x + 1)
    result = run(
        eq_cuadratica, _params(gx, 1.0), x0=1.0, tol=1e-10, max_iter=2
    )

    assert result.applicable is True
    assert result.converged is False
    assert result.root is None
    assert result.iteration_count == 2
