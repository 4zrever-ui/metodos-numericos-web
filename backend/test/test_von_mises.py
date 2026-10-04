import math

import pytest

from backend.methods.von_mises import run


def test_iteraciones_error_porcentual_y_derivada_constante(
    eq_cuadratica, params_x0_valido
):
    result = run(eq_cuadratica, params_x0_valido, x0=1.0)
    rows = {row.k: row for row in result.iterations}

    assert result.applicable is True
    assert [rows[k].x_new for k in (0, 1, 2, 3, 4)] == pytest.approx(
        [3 / 2, 11 / 8, 183 / 128, 46127 / 32768, 3042762591 / 2147483648],
        rel=0.0, abs=1e-12,
    )
    assert [rows[k].error_pct for k in (0, 1, 2, 3, 4)] == pytest.approx(
        [100 / 3, 100 / 11, 700 / 183, 72100 / 46127, 1978351900 / 3042762591],
        rel=0.0, abs=1e-9,
    )
    assert all(row.fp_x0 == 2.0 for row in result.iterations)
    assert result.converged is True
    assert result.iterations[-1].k == 17
    assert result.root == pytest.approx(math.sqrt(2), rel=0.0, abs=1e-6)


def test_tolerancia_laxa_detiene_en_k2_y_devuelve_x_new(
    eq_cuadratica, params_x0_valido
):
    result = run(eq_cuadratica, params_x0_valido, x0=1.0, tol=5)

    assert result.converged is True
    assert len(result.iterations) == 3
    assert result.iterations[-1].k == 2
    assert result.root == pytest.approx(183 / 128, rel=0.0, abs=1e-12)
    assert result.root != pytest.approx(11 / 8, rel=0.0, abs=1e-12)


def test_derivada_cero_inaplicable(
    eq_cuadratica, params_x0_derivada_cero
):
    result = run(eq_cuadratica, params_x0_derivada_cero, x0=0.0)

    assert result.applicable is False
    assert result.iterations == []
    assert result.root is None
    assert result.converged is False
    assert "División por cero" in result.reason


def test_tolerancia_estricta_sin_convergencia_no_devuelve_raiz(
    eq_cuadratica, params_x0_valido
):
    result = run(eq_cuadratica, params_x0_valido, x0=1.0, tol=1e-10)

    assert result.applicable is True
    assert result.converged is False
    assert result.root is None
    assert len(result.iterations) == 25
