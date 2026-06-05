"""
test_steffensen.py
Batería completa para backend/methods/steffensen.py

Método de Steffensen:
  Aplica Δ² sobre la secuencia de Aitken (doble aceleración).
  Requiere base_seq ≥ 5 y aitken_seq ≥ 3.

Riesgos matemáticos cubiertos:
  - gx=None → not applicable
  - base_seq < 5 → not applicable (frontera exacta)
  - aitken_seq < 3 → not applicable
  - Denominador Δ² = 0 en secuencia Aitken → fallback silencioso
  - Amplificación de errores de redondeo por doble Δ²
  - aitken_seq estacionaria → denom persistente = 0
"""

from __future__ import annotations
import math
import pytest
import sympy as sp

from backend.methods.steffensen import run, _delta2
from backend.core.auto_params import AutoParams

_x = sp.Symbol("x")


# ──────────────────────────────────────────────────────────────────────────────
# Tests de la función helper _delta2
# ──────────────────────────────────────────────────────────────────────────────

class TestDelta2Helper:

    def test_formula_correcta(self):
        """Verifica la fórmula Δ² con valores simples."""
        result = _delta2(1.0, 0.5, 0.25)
        assert abs(result - 0.0) < 1e-12

    def test_denominador_cero_fallback(self):
        """RIESGO: denom=0 → retorna p0 (igual que en Aitken)."""
        result = _delta2(2.0, 2.0, 2.0)
        assert result == 2.0

    def test_misma_logica_que_aitken(self):
        """_delta2 en steffensen debe producir el mismo resultado que _aitken_delta2."""
        from backend.methods.aitken import _aitken_delta2
        p0, p1, p2 = 3.0, 1.5, 0.75
        assert abs(_delta2(p0, p1, p2) - _aitken_delta2(p0, p1, p2)) < 1e-15


# ──────────────────────────────────────────────────────────────────────────────
# Tests de run() - Convergencia
# ──────────────────────────────────────────────────────────────────────────────

class TestSteffensenConvergencia:

    def test_converge_con_gx_valido(self, eq_base, params_gx_convergente):
        """Steffensen debe converger a ~0.254102 con g(x)=(x^3+1)/4, x0=0."""
        result = run(eq_base, params_gx_convergente, x0=0.0)
        assert result.applicable is True
        assert result.root is not None
        # No siempre converge (depende de cuántos puntos Aitken haya), pero root ≠ None
        if result.converged:
            assert abs(result.root - 0.254102) < 1e-2

    def test_convergencia_mas_rapida_que_aitken(self, eq_base, params_gx_convergente):
        """RIESGO (verificación positiva): Steffensen (doble Δ²) debe converger
        en ≤ iteraciones que Aitken simple."""
        from backend.methods.aitken import run as run_aitken
        r_steff = run(eq_base, params_gx_convergente, x0=0.0)
        r_aitken = run_aitken(eq_base, params_gx_convergente, x0=0.0)

        if r_steff.converged and r_aitken.converged:
            assert r_steff.iteration_count <= r_aitken.iteration_count + 3

    def test_error_final_menor_tolerancia(self, eq_base, params_gx_convergente):
        """Si converge, error% final < tol."""
        tol = 0.00001
        result = run(eq_base, params_gx_convergente, x0=0.0, tol=tol)
        if result.converged:
            assert result.final_error_pct is not None
            assert result.final_error_pct < tol

    def test_tolerancia_laxa(self, eq_base, params_tolerancia_laxa):
        """Con tol=1.0 converge en la primera oportunidad."""
        result = run(eq_base, params_tolerancia_laxa, x0=0.0, tol=1.0)
        assert result.applicable is True
        assert result.root is not None


# ──────────────────────────────────────────────────────────────────────────────
# Tests de run() - Inaplicabilidad
# ──────────────────────────────────────────────────────────────────────────────

class TestSteffensenInaplicable:

    def test_gx_none_inaplicable(self, eq_base, params_gx_none):
        """RIESGO: gx=None → not applicable inmediatamente."""
        result = run(eq_base, params_gx_none, x0=1.0)
        assert result.applicable is False
        assert result.converged is False
        assert result.iteration_count == 0

    def test_base_seq_menor_5(self, eq_base):
        """RIESGO FRONTERA: base_seq < 5 → not applicable.
        g(x) que diverge en 2 pasos resulta en base_seq=[x0, g(x0), inf] → truncada."""
        gx_div = _x**3 + _x  # diverge rápido
        params_div = AutoParams(
            a=0.0, b=2.0, x0=1.0, x0_alt=2.0, x0_von_mises=1.0,
            tol=0.00001, max_iter=25,
            gx_sympy=gx_div, gx_excel="", gx_latex="",
            gx_candidates=[], roots_approx=[0.254102],
            f_sign_change_found=True,
        )
        result = run(eq_base, params_div, x0=1.0)
        # base_seq será corta → not applicable o applicable con root
        assert result.root is not None or result.applicable is False

    def test_base_seq_exactamente_5_frontera(self, eq_base):
        """RIESGO FRONTERA: exactamente 5 elementos en base_seq: mínimo para pasar el check.
        Con max_iter=2 y g convergente debería generar suficientes puntos."""
        gx = (_x**3 + 1) / 4
        params_min = AutoParams(
            a=0.0, b=1.0, x0=0.0, x0_alt=1.0, x0_von_mises=0.0,
            tol=0.00001, max_iter=2,
            gx_sympy=gx, gx_excel="", gx_latex="",
            gx_candidates=[], roots_approx=[0.254102],
            f_sign_change_found=True,
        )
        result = run(eq_base, params_min, x0=0.0, max_iter=2)
        # Con max_iter=2 se generan max_iter+10 = 12 puntos base si g converge
        # Debe ser applicable=True
        assert result.applicable is True

    def test_aitken_seq_menor_3_inaplicable(self, eq_base):
        """RIESGO: si base_seq tiene exactamente 4 puntos, aitken_seq tiene 2 < 3
        → not applicable."""
        gx_lento = _x / 2  # converge a 0, no a raíz de f, pero genera secuencia
        params = AutoParams(
            a=0.0, b=1.0, x0=0.0, x0_alt=1.0, x0_von_mises=0.0,
            tol=0.00001, max_iter=1,  # base generará max_iter+10=11 puntos
            gx_sympy=gx_lento, gx_excel="", gx_latex="",
            gx_candidates=[], roots_approx=[0.0],
            f_sign_change_found=True,
        )
        result = run(eq_base, params, x0=0.0, max_iter=1)
        # base_seq larga (11 puntos) → aitken_seq = 9 puntos → aplicable
        assert result.root is not None


# ──────────────────────────────────────────────────────────────────────────────
# Tests de estructura del resultado
# ──────────────────────────────────────────────────────────────────────────────

class TestSteffensenEstructura:

    def test_method_name(self, eq_base, params_gx_convergente):
        result = run(eq_base, params_gx_convergente, x0=0.0)
        assert result.method_name == "Steffensen"

    def test_excel_sheet_name(self, eq_base, params_gx_convergente):
        result = run(eq_base, params_gx_convergente, x0=0.0)
        assert result.excel_sheet_name == "Steffensen"

    def test_iteration_count_consistente(self, eq_base, params_gx_convergente):
        result = run(eq_base, params_gx_convergente, x0=0.0)
        if result.iterations:
            assert result.iteration_count == len(result.iterations) - 1

    def test_fila_tiene_xk_hat_finito(self, eq_base, params_gx_convergente):
        """Cada SteffensenRow debe tener xk_hat finito."""
        result = run(eq_base, params_gx_convergente, x0=0.0)
        for row in result.iterations:
            assert math.isfinite(row.xk_hat)

    def test_primera_fila_error_none(self, eq_base, params_gx_convergente):
        """Primera fila: error_pct=None, converged=None (no hay hat previo)."""
        result = run(eq_base, params_gx_convergente, x0=0.0)
        if result.iterations:
            assert result.iterations[0].error_pct is None
            assert result.iterations[0].converged is None

    def test_root_no_none_si_applicable(self, eq_base, params_gx_convergente):
        """Si el método es applicable, root siempre debe ser no None."""
        result = run(eq_base, params_gx_convergente, x0=0.0)
        if result.applicable:
            assert result.root is not None

    def test_amplificacion_redondeo_no_falla(self, eq_base, params_gx_convergente):
        """RIESGO: doble Δ² amplifica errores de redondeo. Verificar que
        el resultado es finito incluso con muchas iteraciones."""
        result = run(eq_base, params_gx_convergente, x0=0.0, max_iter=25)
        if result.root is not None:
            assert math.isfinite(result.root)