"""
test_method_all_params.py — G6: "Resolver todos" debe respetar los parámetros
manuales (igual que el endpoint individual y que el Excel).

Cubre la capa endpoint (method_all), que hasta ahora no estaba testeada:
  - g(x) manual → punto_fijo lo usa (no el auto).
  - intervalo [a,b] manual → bisección lo usa.

Estrategia: contraste sobre la MISMA ecuación cambiando solo el parámetro
manual, de modo que el resultado distinto pruebe que el manual fue aplicado
(independiente de lo que elija auto_params).
"""

from __future__ import annotations
import pytest

from backend.main import method_all


def _result(out: dict, method_key: str) -> dict:
    return next(r for r in out["results"] if r["method"] == method_key)


def test_method_all_respeta_gx_manual():
    """f(x)=x^3-4x+1, raíz 0.254102. g(x)=(x^3+1)/4 converge; g(x)=x^3+x diverge.
    Mismo equation, solo cambia g(x): el resultado distinto prueba que se usa el manual."""
    conv = _result(method_all({"equation": "x**3 - 4*x + 1", "gx": "(x**3 + 1)/4", "x0": 0.5}), "punto_fijo")
    assert conv["applicable"] and conv["converged"]
    assert conv["root"] == pytest.approx(0.254102, abs=1e-3)

    div = _result(method_all({"equation": "x**3 - 4*x + 1", "gx": "x**3 + x", "x0": 0.5}), "punto_fijo")
    assert not div["converged"]


def test_method_all_respeta_intervalo_manual():
    """f(x)=x^2-4, raíces ±2. [1,3] bracketea +2; [3,5] no cambia de signo.
    Mismo equation, solo cambia [a,b]: el resultado distinto prueba que se usa el manual."""
    ok = _result(method_all({"equation": "x**2 - 4", "a": 1, "b": 3}), "biseccion")
    assert ok["applicable"] and ok["converged"]
    assert ok["root"] == pytest.approx(2.0, abs=1e-3)

    no = _result(method_all({"equation": "x**2 - 4", "a": 3, "b": 5}), "biseccion")
    assert not no["converged"]
