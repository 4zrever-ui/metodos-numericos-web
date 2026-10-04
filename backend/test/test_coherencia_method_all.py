import math

import pytest

from backend.main import method_all


# Mismos 11 payloads que audit_method_all.py; gx y tol se omiten.
# Los evaluadores son independientes del parser y de los métodos del backend.
CASES = [
    (1, "x^2-2", 1.0, 2.0, 0.0, 2.0, lambda x: x*x - 2),
    (2, "2*x", 1.0, 2.0, -1.0, 1.0, lambda x: 2*x),
    (3, "x^3", 1.0, 2.0, -1.0, 1.0, lambda x: x*x*x),
    (4, "(x-1)^2", 3.0, 4.0, 0.0, 2.0, lambda x: (x-1)*(x-1)),
    (5, "ln(x)", 3.0, 4.0, 0.5, 3.0, math.log),
    (6, "x^2+1", 1.0, 2.0, -1.0, 1.0, lambda x: x*x + 1),
    (7, "x^3-2*x+2", 0.0, 1.0, -3.0, -1.0, lambda x: x*x*x - 2*x + 2),
    (8, "x^2-2", 0.0, 1.0, 0.0, 2.0, lambda x: x*x - 2),
    (9, "x", 1.0, 2.0, -1.0, 1.0, lambda x: x),
    (10, "atan(x)", 2.0, 3.0, -1.0, 2.0, math.atan),
    (11, "x^2-2", 1.4142135623730951, 1.5, 1.0, 2.0, lambda x: x*x - 2),
]
METHODS = (
    "newton", "biseccion", "regula_falsi", "secante", "punto_fijo",
    "steffensen", "aitken", "von_mises", "newton_modificado",
    "newton_segundo_orden", "chebyshev", "halley", "super_halley", "ostrowsky",
)
EVALUATORS = {case_id: evaluate for case_id, *_, evaluate in CASES}

EXPECTED_FAILURES = {
    (7, "steffensen"): "H9: declara convergencia en 0.5 con |f(root)|=1.125.",
    (7, "aitken"): "H9: declara convergencia en 0.5 con |f(root)|=1.125.",
    (10, "secante"): "H10: declara convergencia con |atan(root)| cercano a pi/2.",
    (5, "secante"): "H7: declara convergencia con root fuera del dominio de ln.",
    (8, "newton"): "H11: devuelve root=0.0 aunque converged=False.",
}


def _case_method_param(case_id, method):
    reason = EXPECTED_FAILURES.get((case_id, method))
    marks = [pytest.mark.xfail(strict=True, reason=reason)] if reason else []
    return pytest.param(
        case_id, method, marks=marks, id=f"caso-{case_id:02d}-{method}"
    )


@pytest.fixture(scope="module")
def results_by_case():
    results = {}
    for case_id, equation, x0, x1, a, b, _ in CASES:
        payload = {
            "equation": equation, "x0": x0, "x1": x1, "a": a, "b": b,
        }
        response = method_all(payload)
        assert len(response["results"]) == len(METHODS)
        results[case_id] = {
            result["method"]: result for result in response["results"]
        }
        assert set(results[case_id]) == set(METHODS)
    return results


# C no se comprueba por este camino: method_all captura las excepciones
# de cada método y las devuelve como N/A (applicable=False).
@pytest.mark.parametrize(
    "case_id,method",
    [
        _case_method_param(case_id, method)
        for case_id, *_ in CASES
        for method in METHODS
    ],
)
def test_coherencia_convergencia_y_raiz(case_id, method, results_by_case):
    result = results_by_case[case_id][method]
    root = result["root"]

    if result["converged"] is False:
        assert root is None, (
            f"Caso {case_id}, {method}: sin convergencia, root={root!r}."
        )
        return

    assert result["converged"] is True
    assert root is not None
    assert math.isfinite(root)
    try:
        residual = abs(EVALUATORS[case_id](root))
    except (ValueError, OverflowError, ZeroDivisionError, TypeError) as exc:
        pytest.fail(
            f"Caso {case_id}, {method}: f({root!r}) no evaluable: {exc}",
            pytrace=False,
        )
    assert math.isfinite(residual)
    assert residual <= 1e-6, (
        f"Caso {case_id}, {method}: root={root!r}, |f(root)|={residual!r}."
    )
