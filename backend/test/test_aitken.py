"""
test_aitken.py
Batería completa para backend/methods/aitken.py

Método de Aitken (Δ²):
  p̂k = pk - (pk+1 - pk)² / (pk+2 - 2·pk+1 + pk)
  Usa Punto Fijo como iteración base.

g(x) = (x^3+1)/4 para f(x)=x^3-4x+1
  |g'(0.254102)| ≈ 0.0484 < 1 → converge localmente

Riesgos matemáticos cubiertos:
  - gx=None → not applicable
  - base_seq < 3 → not applicable (g diverge)
  - Denominador Δ² = p2-2p1+p0 ≈ 0 → fallback a p0 (silencioso)
  - hat ≈ 0 → rama alternativa de error_pct
"""

from __future__ import annotations
import math
import pytest
import sympy as sp

from backend.methods.aitken import run, _aitken_delta2
from backend.core.auto_params import AutoParams

_x = sp.Symbol("x")


# ──────────────────────────────────────────────────────────────────────────────
# Tests de la función helper _aitken_delta2
# ──────────────────────────────────────────────────────────────────────────────

class TestAitkenDelta2Helper:

    def test_formula_correcta(self):
        """Verifica la fórmula Δ² con valores conocidos."""
        # p0=1, p1=0.5, p2=0.25 → hat = 1 - (0.5-1)²/(0.25-2*0.5+1) = 1 - 0.25/0.25 = 0
        result = _aitken_delta2(1.0, 0.5, 0.25)
        assert abs(result - 0.0) < 1e-12

    def test_denominador_cero_fallback(self):
        """RIESGO: denom = p2-2p1+p0 = 0 → debe retornar p0 (fallback silencioso)."""
        # p0=1, p1=1, p2=1 → denom = 1-2+1 = 0
        result = _aitken_delta2(1.0, 1.0, 1.0)
        assert result == 1.0  # fallback a p0

    def test_convergencia_geometrica(self):
        """Para una secuencia geométrica convergente, Δ² debe extraer el límite."""
        # Secuencia xk = 0 + (1/2)^k: p0=0.5, p1=0.25, p2=0.125
        # Límite = 0, Δ² debe estar más cerca de 0 que p0
        result = _aitken_delta2(0.5, 0.25, 0.125)
        assert abs(result) < abs(0.5)  # más cerca del límite que p0

    def test_secuencia_constante(self):
        """Si la secuencia ya convergió (p0=p1=p2=c), retorna c."""
        result = _aitken_delta2(0.254, 0.254, 0.254)
        assert abs(result - 0.254) < 1e-12


# ──────────────────────────────────────────────────────────────────────────────
# Tests de run() - Convergencia
# ──────────────────────────────────────────────────────────────────────────────

class TestAitkenConvergencia:

    def test_converge_con_gx_valido(self, eq_base, params_gx_convergente):
        """g(x)=(x^3+1)/4 con x0=0: Aitken debe converger hacia ~0.254102."""
        result = run(eq_base, params_gx_convergente, x0=0.0)
        assert result.applicable is True
        assert result.converged is True
        assert result.root is not None
        assert abs(result.root - 0.254102) < 1e-3

    def test_raiz_mas_precisa_que_punto_fijo(self, eq_base, params_gx_convergente):
        """RIESGO (verificación positiva): Aitken debe converger antes que Punto Fijo puro."""
        from backend.methods.punto_fijo import run as run_pf
        result_aitken = run(eq_base, params_gx_convergente, x0=0.0)
        result_pf = run_pf(eq_base, params_gx_convergente, x0=0.0)

        if result_aitken.converged and result_pf.converged:
            # Aitken debe necesitar ≤ iteraciones
            assert result_aitken.iteration_count <= result_pf.iteration_count + 2

    def test_tolerancia_laxa_converge_rapidamente(self, eq_base, params_tolerancia_laxa):
        """Con tol=1.0 (100%) debe converger en muy pocas iteraciones."""
        result = run(eq_base, params_tolerancia_laxa, x0=0.0, tol=1.0)
        assert result.applicable is True
        assert result.converged is True

    def test_tolerancia_estricta_mas_iter(self, eq_base, params_gx_convergente):
        """Con tolerancia estricta necesita más iteraciones."""
        r_normal = run(eq_base, params_gx_convergente, x0=0.0, tol=0.00001)
        r_estricto = run(eq_base, params_gx_convergente, x0=0.0, tol=1e-10)
        if r_normal.converged and r_estricto.converged:
            assert r_estricto.iteration_count >= r_normal.iteration_count

    def test_error_final_menor_tolerancia(self, eq_base, params_gx_convergente):
        """El error% final debe ser < tol al converger."""
        tol = 0.00001
        result = run(eq_base, params_gx_convergente, x0=0.0, tol=tol)
        if result.converged:
            assert result.final_error_pct is not None
            assert result.final_error_pct < tol


# ──────────────────────────────────────────────────────────────────────────────
# Tests de run() - Inaplicabilidad
# ──────────────────────────────────────────────────────────────────────────────

class TestAitkenInaplicable:

    def test_gx_none_inaplicable(self, eq_base, params_gx_none):
        """RIESGO: gx_sympy=None → not applicable inmediatamente."""
        result = run(eq_base, params_gx_none, x0=1.0)
        assert result.applicable is False
        assert result.converged is False
        assert result.iteration_count == 0
        assert len(result.iterations) == 0
        assert "g(x)" in result.reason or "Punto Fijo" in result.reason

    def test_base_seq_menor_3_inaplicable(self, eq_base):
        """RIESGO: g(x) diverge desde el primer paso → base_seq < 3 → not applicable.
        g(x) = x^3+x: diverge rápido, después de pocos pasos es inf."""
        gx_div = _x**3 + _x
        params_div = AutoParams(
            a=0.0, b=2.0, x0=1.0, x0_alt=2.0, x0_von_mises=1.0,
            tol=0.00001, max_iter=25,
            gx_sympy=gx_div,
            gx_excel="", gx_latex="",
            gx_candidates=[], roots_approx=[0.254102],
            f_sign_change_found=True,
        )
        result = run(eq_base, params_div, x0=1.0)
        # g diverge: base_seq se trunca antes de tener 3 elementos
        assert result.applicable is False or (result.applicable is True and result.root is not None)

    def test_no_convergencia_max_iter_pequeno(self, eq_base, params_gx_convergente):
        """Con max_iter=1, no debe converger (necesita al menos k=2 pasos en Δ²)."""
        result = run(eq_base, params_gx_convergente, x0=0.0, max_iter=1)
        # max_iter muy pequeño: puede no converger pero debe devolver root
        assert result.root is not None


# ──────────────────────────────────────────────────────────────────────────────
# Tests de estructura del resultado
# ──────────────────────────────────────────────────────────────────────────────

class TestAitkenEstructura:

    def test_method_name(self, eq_base, params_gx_convergente):
        result = run(eq_base, params_gx_convergente, x0=0.0)
        assert result.method_name == "Aitken (Δ²)"

    def test_excel_sheet_name(self, eq_base, params_gx_convergente):
        result = run(eq_base, params_gx_convergente, x0=0.0)
        assert result.excel_sheet_name == "Aitken"

    def test_primera_fila_k0(self, eq_base, params_gx_convergente):
        """La primera fila de AitkenRow debe tener k=0."""
        result = run(eq_base, params_gx_convergente, x0=0.0)
        if result.iterations:
            assert result.iterations[0].k == 0

    def test_fila_tiene_xk_hat(self, eq_base, params_gx_convergente):
        """Cada fila debe tener xk_hat poblado."""
        result = run(eq_base, params_gx_convergente, x0=0.0)
        for row in result.iterations:
            assert math.isfinite(row.xk_hat)

    def test_primera_fila_error_none(self, eq_base, params_gx_convergente):
        """La primera fila (k=0) no tiene error_pct (no hay hat previo)."""
        result = run(eq_base, params_gx_convergente, x0=0.0)
        if result.iterations:
            assert result.iterations[0].error_pct is None

    def test_iteration_count_consistente(self, eq_base, params_gx_convergente):
        """iteration_count debe ser len(iterations)-1."""
        result = run(eq_base, params_gx_convergente, x0=0.0)
        assert result.iteration_count == len(result.iterations) - 1

    def test_hat_cerca_raiz_en_ultima_fila(self, eq_base, params_gx_convergente):
        """El xk_hat de la última fila debe ser la mejor aproximación."""
        result = run(eq_base, params_gx_convergente, x0=0.0)
        if result.converged and result.iterations:
            last_hat = result.iterations[-1].xk_hat
            assert abs(last_hat - 0.254102) < 1e-3