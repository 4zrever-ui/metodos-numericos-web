import math

import pytest

from backend.methods.secante import run


def test_iteraciones_y_error_porcentual(eq_cuadratica, params_secante_valido):
    result = run(
        eq_cuadratica, params_secante_valido, x0=1.0, x1=2.0, tol=1e-10
    )
    rows = {row.k: row for row in result.iterations}

    assert result.applicable is True
    assert rows[0].error_pct is None
    assert rows[0].x_new == 1.0
    assert [rows[k].x_new for k in (1, 2, 3, 4)] == pytest.approx(
        [4 / 3, 7 / 5, 58 / 41, 816 / 577], rel=0.0, abs=1e-12
    )
    assert [rows[k].error_pct for k in (1, 2, 3, 4)] == pytest.approx(
        [50, 100 / 21, 30 / 29, 125 / 4182], rel=0.0, abs=1e-9
    )
    assert result.converged is True
    assert result.root == pytest.approx(math.sqrt(2), rel=0.0, abs=1e-10)


def test_tolerancia_laxa_detiene_en_k4_y_devuelve_x_new(
    eq_cuadratica, params_secante_valido
):
    result = run(
        eq_cuadratica, params_secante_valido, x0=1.0, x1=2.0, tol=1.0
    )

    assert result.applicable is True
    assert result.converged is True
    assert result.iteration_count == 4
    assert result.root == pytest.approx(816 / 577, rel=0.0, abs=1e-12)
    assert result.root != pytest.approx(58 / 41, rel=0.0, abs=1e-12)


def test_convergencia_en_k1_devuelve_x2(eq_cuadratica, params_secante_valido):
    result = run(
        eq_cuadratica, params_secante_valido, x0=1.0, x1=2.0, tol=60
    )

    assert result.converged is True
    assert result.iteration_count == 1
    assert result.root == pytest.approx(4 / 3, rel=0.0, abs=1e-12)
    assert len(result.iterations) == 2


def test_denominador_cero_en_k1_inaplicable(eq_cuadratica, params_secante_valido):
    result = run(
        eq_cuadratica, params_secante_valido, x0=-2.0, x1=2.0
    )

    assert result.applicable is False
    assert result.root is None
    assert result.iteration_count == 0


def test_max_iter_sin_convergencia_no_devuelve_raiz(
    eq_cuadratica, params_secante_valido
):
    result = run(
        eq_cuadratica, params_secante_valido,
        x0=1.0, x1=2.0, tol=1e-10, max_iter=2,
    )

    assert result.applicable is True
    assert result.converged is False
    assert result.root is None
    assert result.iteration_count == 2
